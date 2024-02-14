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
    start_time = models.DateTimeField(blank=False, null=True)  # Время начала рассылки
    text = models.TextField(blank=False, null=True, default='Удалите этот текст перед отправкой')
    clients = models.ManyToManyField(Clients, blank=False, null=True)
    end_time = models.DateTimeField(blank=False, null=True)  # Время окончания рассылки
    STATUS_CHOICES = (
        ('open', 'Открыт'),
        ('working', 'В работе'),
        ('archived', 'Архив'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def formatted_start_time(self):
        return timezone.localtime(self.start_time).strftime("%Y-%m-%d %H:%M:%S")

    def formatted_end_time(self):
        return timezone.localtime(self.end_time).strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        return f'{self.pk}, Start_time: {self.start_time}, end_time: {self.end_time}'
