from rest_framework import serializers
from .models import Messages


class MessageSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'
