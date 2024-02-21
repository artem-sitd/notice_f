import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notice_f.settings')
import config
import logging.config
import requests
import time
from clients.models import Clients
from messages_app.models import Messages
from mailings.models import Mailing
from celery import shared_task
from django.utils import timezone

logging.config.dictConfig(config.dict_config_celery)
logger = logging.getLogger(__name__)

url = 'https://probe.fbrq.cloud/v1/send'
headers = {
    'Authorization': f'Bearer {config.TOKEN}',
    'Content-Type': 'application/json'
}


def send_request_with_retry(url, payload, headers, max_retries=3, retry_delay=5):
    logger.info('Вход в send_request_with_retry')
    for i in range(max_retries):
        try:
            logger.info(f'send_request_with_retry попытка обращения к {url}')
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()  # Проверка на ошибки HTTP
            logger.info(f'send_request_with_retry response= {response}')
            return response, None  # Возвращаем успешный ответ
        except requests.exceptions.Timeout:
            logger.error(f'send_request_with_retry ошибка по timeout, была попытка {i}')
            print(f"Превышено время ожидания при обращении к {url}, попытка {i + 1}")
            if i < max_retries - 1:
                print(f'Повторная попытка через {retry_delay} секунд')
                logger.info(f'send_request_with_retry повторная попытка через {retry_delay} секунд')

                time.sleep(retry_delay)
            else:
                logger.error('send_request_with_retry Достигнуто максимальное количество попыток, запрос не выполнен')
                print('Достигнуто максимальное количество попыток, запрос не выполнен')
                return None, f"Превышено время ожидания при обращении к {url}, после {max_retries} попыток"
        except requests.exceptions.RequestException as er:
            logger.error(f'send_request_with_retry Ошибка при выполнении запроса RequestException: {str(er)}')
            print(f'Ошибка при выполнении запроса RequestException: {str(er)}')
            if i < max_retries - 1:
                print(f'Повторная попытка через {retry_delay} секунд')
                logger.info(f'send_request_with_retry повторная попытка через {retry_delay} секунд')
                time.sleep(retry_delay)
            else:
                logger.error('send_request_with_retry Достигнуто максимальное количество попыток, запрос не выполнен')
                print('Достигнуто максимальное количество попыток, запрос не выполнен')
                return None, f'RequestException {str(er)}'


@shared_task(bind=True, retry_backoff=300)
def start_mailing(*args, **kwargs):
    logger.info('Вход в start_mailing')
    try:
        logger.info('start_mailing проверка токена')
        current_time = timezone.now()
        if not config.TOKEN:
            logger.error('start_mailing ТОКЕН НЕ ЗАГРУЖЕН')
            return 'апи токен не загружен'
        logger.info('start_mailing фильтруем Mailing для рассылок')
        mailings = Mailing.objects.prefetch_related('clients').filter(
            status='open',
            start_time__lte=current_time,
            end_time__gte=current_time
        )
        if not mailings:
            logger.info('start_mailing готовых Mailing для рассылок не найдено')
            return 'Нет готовых к отправке рассылок'
        for mailing in mailings:
            logger.info('start_mailing Mailing найдены, производим подготовку')
            mailing.status = 'working'
            mailing.save()
            payload = {}
            id = mailing.id
            text = mailing.text
            payload['id'] = id
            payload['text'] = text
            phones = [client.mobile_code + client.phone for client in mailing.clients.all()]
            logger.info('start_mailing Mailing найдены, производим подготовку клиентов (номеров телефонов)')
            for phone in phones:
                payload['phone'] = phone
                client = Clients.objects.filter(phone=phone[3:]).only('id').first()
                try:
                    logger.info(
                        f'start_mailing обращаемся к send_request_with_retry, url={url}/{id}, pauload={payload},'
                        f' headers={headers}')
                    response, error = send_request_with_retry(f'{url}/{id}', payload, headers)
                    if response and response.status_code == 200:
                        logger.info('start_mailing статус код ответа от сервиса 200, создаем Messages')
                        print(f'Запрос успешно выполнен {payload}')
                        new_message = Messages.objects.create(status=True, client=client, mailings=mailing)
                        new_message.save()
                        print('Создано сообщение:', new_message)
                    else:
                        logger.error(f'start_mailing ошибка запроса {error}')
                        print(f'Ошибка выполнения запроса {payload}, error: {error}')
                        logger.info('start_mailing создаем Messages status=False')
                        new_message = Messages.objects.create(status=False, client=client, mailings=mailing,
                                                              error=error)
                        new_message.save()
                except Exception as e:
                    logger.error(f'start_mailing ошибка запроса: {e}')
                    print(f'Ошибка при выполнении запроса: {payload},ошибка: {e}')
            logger.info('start_mailing mailing.status = archived')
            mailing.status = 'archived'
            mailing.save()
        return 'Рассылки завершены'
    except Exception as exc:
        logger.info(f'start_mailing ошибка в конце {exc}, задача будет перезапушена через 5 минут')
    #     # Если возникает ошибка, Celery автоматически повторно запустит эту задачу через указанное время
    #     raise self.retry(exc=exc,
    #                      countdown=300)  # countdown=300 означает, что задача будет повторно запущена через 5 минут
