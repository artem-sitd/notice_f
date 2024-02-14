from rest_framework import serializers
from .models import Mailing
from django.utils import timezone
from datetime import timedelta


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'

    def validate_start_time(self, value):
        # Проверяем соответствие формата данных
        try:
            formatted_start_time = timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            raise serializers.ValidationError(
                {"start_time": ["Некорректный формат времени, необходимо использовать %Y-%m-%d %H:%M:%S"]})

        # Проверяем разницу во времени
        current_time = timezone.now()
        if value - current_time < timedelta(minutes=10):
            raise serializers.ValidationError(
                f"Разница во времени должна быть не менее 5 минут, текущее время: {current_time}")
        return value

    def validate_end_time(self, value):
        # Проверяем соответствие формата данных
        try:
            formatted_end_time = timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            raise serializers.ValidationError(
                {"end_time": ["Некорректный формат времени, необходимо использовать %Y-%m-%d %H:%M:%S"]})

        # Дополнительная проверка разницы между start_time и end_time
        if value - self.initial_data['start_time'] < timedelta(minutes=10):
            raise serializers.ValidationError("Разница между start_time и end_time должна быть не менее 10 минут")
        return value
