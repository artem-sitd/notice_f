import logging.config
from config import dict_config
from rest_framework import serializers
from .models import Clients, Tag

logging.config.dictConfig(dict_config)
logger = logging.getLogger(__name__)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'

    def validate_phone(self, value):
        logger.info('Вход в ClientSerializer (validate_phone)')
        """
        Пользовательский метод валидации для поля phone.
        Проверяет, что номер телефона содержит только цифры и имеет длину 7 символов.
        """
        if not value.isdigit() or len(value) != 7:
            logger.error('ClientSerializer (validate_phone) - "Неправильный формат номера телефона"')
            raise serializers.ValidationError("Неправильный формат номера телефона")
        if Clients.objects.filter(phone=value).exists():
            logger.error('ClientSerializer (validate_phone) - Номер телефона уже существует')
            raise serializers.ValidationError("Номер телефона уже существует")
        logger.info('ClientSerializer (validate_phone) проверка пройдена')
        return value

    def validate_timezone(self, value):
        logger.info('Вход в ClientSerializer (validate_timezone)')
        """
        Пользовательский метод валидации для поля timezone.
        Проверяет, что значение поля находится в списке допустимых значений.
        """
        valid_timezones = ['Europe/Kaliningrad', 'Europe/Moscow', 'Europe/Samara', 'Asia/Yekaterinburg', 'Asia/Omsk',
                           'Asia/Krasnoyarsk', 'Asia/Irkutsk', 'Asia/Yakutsk', 'Asia/Vladivostok', 'Asia/Magadan',
                           'Asia/Kamchatka']
        if value not in valid_timezones:
            logger.error(
                'ClientSerializer (validate_timezone) указан не верный часовой пояс (читайте в swagger какие есть)')
            raise serializers.ValidationError("Недопустимое значение часового пояса")
        logger.info('ClientSerializer (validate_timezone) - проверка пройдена')
        return value

    def validate_mobile_code(self, value):
        logger.info('Вход в ClientSerializer (validate_mobile_code)')
        """
        Пользовательский метод валидации для поля mobile_code.
        Проверяет, что код мобильного оператора содержит только цифры и имеет длину 3 символа.
        """
        if not value.isdigit() or len(value) != 3:
            logger.error('ClientSerializer (validate_mobile_code) длина кода !=3 или указаны не цифры')
            raise serializers.ValidationError("Неправильный формат кода мобильного оператора (максимум 3 цифры")
        logger.error('ClientSerializer (validate_mobile_code) проверка пройдена')
        return value
