import requests
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import generics, status
from drf_spectacular.utils import extend_schema
from clients.models import Clients
from mailings.models import Mailing
from .models import Messages
from config import TOKEN
from .serializers import MessageSeralizer

url = 'https://probe.fbrq.cloud/v1/send'
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}


def send_request_with_retry(url, payload, headers, max_retries=3, retry_delay=5):
    for i in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()  # Проверка на ошибки HTTP
            return response, None  # Возвращаем успешный ответ
        except requests.exceptions.Timeout:
            print(f"Превышено время ожидания при обращении к {url}, попытка {i + 1}")
            if i < max_retries - 1:
                print(f'Повторная попытка через {retry_delay} секунд')
                time.sleep(retry_delay)
            else:
                print('Достигнуто максимальное количество попыток, запрос не выполнен')
                return None, f"Превышено время ожидания при обращении к {url}, после {max_retries} попыток"
        except requests.exceptions.RequestException as er:
            print(f'Ошибка при выполнении запроса RequestException: {str(er)}')
            if i < max_retries - 1:
                print(f'Повторная попытка через {retry_delay} секунд')
                time.sleep(retry_delay)
            else:
                print('Достигнуто максимальное количество попыток, запрос не выполнен')
                return None, f'RequestException {str(er)}'


def start_mailing():
    if not TOKEN:
        return 'апи токен не загружен'
    mailings = Mailing.objects.prefetch_related('clients').filter(status='open')
    if not mailings:
        return 'Нет готовых к отправке рассылок'
    for mailing in mailings:
        payload = {}
        id = mailing.id
        text = mailing.text
        payload['id'] = id
        payload['text'] = text
        phones = [client.mobile_code + client.phone for client in mailing.clients.all()]
        for phone in phones:
            payload['phone'] = phone
            client = Clients.objects.filter(phone=phone[3:]).only('id').first()
            try:
                response, error = send_request_with_retry(f'{url}/{id}', payload, headers)
                if response and response.status_code == 200:
                    print(f'Запрос успешно выполнен {payload}')
                    new_message = Messages.objects.create(status=True, client=client, mailings=mailing)
                    new_message.save()
                    print('Создано сообщение:', new_message)
                else:
                    print(f'Ошибка выполнения запроса {payload}, error: {error}')
                    new_message = Messages.objects.create(status=False, client=client, mailings=mailing,
                                                          error=error)
                    new_message.save()
            except Exception as e:
                print(f'Ошибка при выполнении запроса: {payload},ошибка: {e}')
    return 'Рассылки завершены'


class MessageApi(APIView):
    @extend_schema(description='если передать в конец url id - выведет конкретное собщение, если не передать выведет '
                               'все имеющиеся сообщения из базы')
    def get(self, request: Request, **kwargs) -> Response:
        message_id = kwargs.get('pk')
        if message_id:
            message = generics.get_object_or_404(Messages, id=message_id)
            serialized = MessageSeralizer(message, many=False)
            return Response(serialized.data, status=200)
        message = Messages.objects.all()
        serialized = MessageSeralizer(message, many=True)
        return Response(serialized.data, status=200)


class MessagesStat(APIView):
    def get(self, request: Request) -> Response:
        mailing_id = request.data.get('id')
        if not mailing_id:
            return Response({'error': 'не указан id целевой рассылки'}, status=status.HTTP_400_BAD_REQUEST)
        mailing_instance = Messages.objects.select_related('mailings').filter(mailings=mailing_id)
        if not mailing_instance:
            return Response({'error': 'сообщений по указанной рассылке не найдено'}, status=status.HTTP_400_BAD_REQUEST)
