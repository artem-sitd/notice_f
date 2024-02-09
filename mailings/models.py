"""
Сущность "рассылка" имеет атрибуты:
    уникальный id рассылки
    дата и время запуска рассылки
    текст сообщения для доставки клиенту
    фильтр свойств клиентов, на которых должна быть произведена рассылка (код мобильного оператора, тег)
    дата и время окончания рассылки: если по каким-то причинам не успели разослать все сообщения - никакие
    сообщения клиентам после этого времени доставляться не должны
"""
from django.db import models

from clients.models import Clients
from django.utils import timezone


class Mailing(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    text = models.TextField(blank=False, null=True, default='Удалите этот текст перед отправкой')
    clients = models.ManyToManyField(Clients, blank=False, null=True)
    end_time = models.DateTimeField()

    def formatted_created_at(self):
        return timezone.localtime(self.created_at).strftime("%Y-%m-%d %H:%M:%S")

    def formatted_end_time(self):
        return timezone.localtime(self.end_time).strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        return f'{self.created_at}, {self.end_time}'
