from rest_framework import serializers
from .models import Mailing
from django.utils import timezone
from datetime import timedelta, datetime
import logging.config
from config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger(__name__)


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'

    def validate_start_time(self, value):
        logger.info('вход в MailSerializer (validate_start_time)')
        # Проверяем соответствие формата данных
        try:
            formatted_start_time = value.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            logger.info('MailSerializer (validate_start_time) EXCEPT ValueError - Некорректный формат времени')
            raise serializers.ValidationError(
                {"start_time": ["Некорректный формат времени, необходимо использовать %Y-%m-%d %H:%M:%S"]})

        # Проверяем разницу во времени
        current_time = datetime.now()
        if value - current_time < timedelta(minutes=10):
            logger.info('MailSerializer (validate_start_time) Разница во времени должна быть не менее 5 минут')
            raise serializers.ValidationError(
                f"Разница во времени должна быть не менее 5 минут, текущее время: {current_time}")
        return value

    def validate_end_time(self, value):
        logger.info('вход в MailSerializer (validate_end_time)')
        # Проверяем соответствие формата данных
        try:
            formatted_end_time = value.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            logger.info('MailSerializer (validate_end_time) EXCEPT ValueError - Некорректный формат времени')
            raise serializers.ValidationError(
                {"end_time": ["Некорректный формат времени, необходимо использовать %Y-%m-%d %H:%M:%S"]})

        # Дополнительная проверка разницы между start_time и end_time
        # if value - self.initial_data['start_time'] < timedelta(minutes=10):
        #     logger.info('MailSerializer (validate_end_time) Разница во времени должна быть не менее 5 минут')
        #     raise serializers.ValidationError("Разница между start_time и end_time должна быть не менее 10 минут")
        # return value
        start_time_str = self.initial_data.get('start_time')
        if start_time_str:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            if value - start_time < timedelta(minutes=10):
                logger.info('MailSerializer (validate_end_time) Разница во времени должна быть не менее 5 минут')
                raise serializers.ValidationError("Разница между start_time и end_time должна быть не менее 10 минут")
        return value
