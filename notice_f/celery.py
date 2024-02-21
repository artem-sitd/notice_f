import os
import config
import logging.config
from celery import Celery
from celery.schedules import crontab
from api.tasks import start_mailing
app = Celery("notice_f")

logging.config.dictConfig(config.dict_config_celery)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notice_f.settings")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# можно тут настройки оставить, либо общие в settings.py
app.conf.update(
    CELERY_ENABLE_UTC=True,
)

app.conf.beat_schedule = {
    "start_mailing_every_5_minutes": {
        "task": start_mailing,  # Путь к вашей функции
        "schedule": crontab(minute="*/5"),  # Расписание: каждые 5 минут
    },
}
