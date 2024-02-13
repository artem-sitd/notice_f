import sys
from messages_app.models import Messages
from django.core.management import BaseCommand
from django.contrib.contenttypes.models import ContentType
from config import TOKEN
import requests, time
from mailings.models import Mailing
from clients.models import Clients
import pdb

url = 'https://probe.fbrq.cloud/v1/send'
headers = {
    'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Mzg5Mjk4MzQsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6Imh0dHBzOi8vdC5tZS9hcnRfa2FrX2RlbGEifQ.8eo8bRpbad94wGmrMNnKrh9wjh0DlsYSVOtRwmnbjdA',
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


class Command(BaseCommand):
    def handle(self, *args, **options):
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
