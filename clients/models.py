"""
Сущность "клиент" имеет атрибуты:
уникальный id клиента
номер телефона клиента в формате 7XXXXXXXXXX (X - цифра от 0 до 9)
код мобильного оператора
тег (произвольная метка)
часовой пояс

Europe/Kaliningrad - Калининградское время (UTC+2 в стандартное время).
Europe/Moscow - Московское время (UTC+3 в стандартное время, UTC+4 в летнее время).
Europe/Samara - Самарское время (UTC+4 в стандартное время).
Asia/Yekaterinburg - Екатеринбургское время (UTC+5).
Asia/Omsk - Омское время (UTC+6).
Asia/Krasnoyarsk - Красноярское время (UTC+7).
Asia/Irkutsk - Иркутское время (UTC+8 в стандартное время, UTC+9 в летнее время).
Asia/Yakutsk - Якутское время (UTC+9).
Asia/Vladivostok - Владивостокское время (UTC+10).
Asia/Magadan - Магаданское время (UTC+11).
Asia/Kamchatka - Камчатское время (UTC+12).
"""

from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator


class Tag(models.Model):
    text = models.CharField(max_length=30, blank=False, null=True)

    def __str__(self):
        return f'{self.text}'


class Clients(models.Model):
    TIMEZONE_CHOICES = (
        ('Europe/Kaliningrad', 'Europe/Kaliningrad'),
        ('Europe/Moscow', 'Europe/Moscow'),
        ('Europe/Samara', 'Europe/Samara'),
        ('Asia/Yekaterinburg', 'Asia/Yekaterinburg'),
        ('Asia/Omsk', 'Asia/Omsk'),
        ('Asia/Krasnoyarsk', 'Asia/Krasnoyarsk'),
        ('Asia/Irkutsk', 'Asia/Irkutsk'),
        ('Asia/Yakutsk', 'Asia/Yakutsk'),
        ('Asia/Vladivostok', 'Asia/Vladivostok'),
        ('Asia/Magadan', 'Asia/Magadan'),
        ('Asia/Kamchatka', 'Asia/Kamchatka'),
    )

    phone = models.CharField(max_length=7, blank=False, null=True, unique=True)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, blank=False, null=True)
    timezone = models.CharField(choices=TIMEZONE_CHOICES, blank=False, null=True)
    mobile_code = models.CharField(max_length=3, blank=False, null=True,
                                   validators=[MinLengthValidator(3), MaxLengthValidator(3)])

    def __str__(self) -> str:
        return f'{self.mobile_code}{self.phone}, {self.tag}, {self.timezone}'
