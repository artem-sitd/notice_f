import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
from celery.schedules import crontab
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notice_f.settings')

app = Celery('notice_f')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# можно тут настройки оставить, либо общие в settings.py
app.conf.update(
    CELERY_ENABLE_UTC=True,
)
app.conf.beat_schedule = {
    'update_contracts_validity': {
        'task': 'api.tasks.start_mailing',
        'schedule': crontab(hour='0', minute='0'),  # Задача будет выполняться ежедневно в полночь
    },
    # 'task5sec': {
    #     'task': 'contracts.tasks.test5sec',
    #     'schedule': timedelta(seconds=5),
    # },
    # 'task10sec': {
    #     'task': 'contracts.tasks.test10sec',
    #     'schedule': timedelta(seconds=10)
    # }
}
