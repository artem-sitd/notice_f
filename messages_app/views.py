from mailings.models import Mailing
from .models import Messages
from config import TOKEN


def sending_messages():
    list_mailings = []
    url = 'https://probe.fbrq.cloud/v1'
    for mailing in Mailing.objects.filter(status='open'):
        pass


def check_status():
    pass
