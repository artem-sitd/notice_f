"""
Сущность "сообщение" имеет атрибуты:
    уникальный id сообщения
    дата и время создания (отправки)
    статус отправки
    id рассылки, в рамках которой было отправлено сообщение
    id клиента, которому отправили
"""
from django.db import models
from django.utils import timezone
from mailings.models import Mailing
from clients.models import Clients


class Messages(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    status = models.BooleanField(default=False)  # если True - отправлено
    mailings = models.ForeignKey(Mailing, on_delete=models.SET_NULL, blank=False, null=True)  # рассылка
    client = models.ForeignKey(Clients, on_delete=models.SET_NULL, blank=False, null=True)  # клиент
    errors = models.TextField(null=True)

    def formatted_created_at(self):
        return timezone.localtime(self.created_at).strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        return f'{self.status}, {self.client}, {self.mailings}'
