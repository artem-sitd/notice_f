from rest_framework import serializers
from .models import Clients, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'

    def validate_phone(self, value):
        """
        Пользовательский метод валидации для поля phone.
        Проверяет, что номер телефона содержит только цифры и имеет длину 7 символов.
        """
        if not value.isdigit() or len(value) != 7:
            raise serializers.ValidationError("Неправильный формат номера телефона")
        if Clients.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Номер телефона уже существует")
        return value

    def validate_timezone(self, value):
        """
        Пользовательский метод валидации для поля timezone.
        Проверяет, что значение поля находится в списке допустимых значений.
        """
        valid_timezones = ['Europe/Kaliningrad', 'Europe/Moscow', 'Europe/Samara', 'Asia/Yekaterinburg', 'Asia/Omsk',
                           'Asia/Krasnoyarsk', 'Asia/Irkutsk', 'Asia/Yakutsk', 'Asia/Vladivostok', 'Asia/Magadan',
                           'Asia/Kamchatka']
        if value not in valid_timezones:
            raise serializers.ValidationError("Недопустимое значение часового пояса")
        return value

    def validate_mobile_code(self, value):
        """
        Пользовательский метод валидации для поля mobile_code.
        Проверяет, что код мобильного оператора содержит только цифры и имеет длину 3 символа.
        """
        if not value.isdigit() or len(value) != 3:
            raise serializers.ValidationError("Неправильный формат кода мобильного оператора")
        return value
