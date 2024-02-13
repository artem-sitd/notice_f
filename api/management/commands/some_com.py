from django.core.management import BaseCommand
from django.contrib.contenttypes.models import ContentType
from config import TOKEN
import requests, time
from mailings.models import Mailing
import pdb

url = 'https://probe.fbrq.cloud/v1/send/8'
headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}
payload = {'id': 1, 'text': 'zzzzzzz', 'phone': '7751234560'}


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(TOKEN)
        try:
            pdb.set_trace()
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()  # Проверка на ошибки HTTP
            print(response)
            print(response.text)
            if response:
                print(f'Запрос успешно выполнен {payload}')
            else:
                print(f'Ошибка выполнения запроса {payload}')
        except Exception as e:
            print(f'Ошибка при выполнении запроса: {payload},ошибка: {e}')
