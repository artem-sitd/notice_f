from django.core.management import BaseCommand
import requests
from mailings.models import Mailing
import pdb


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_messages_in_mailing=Mailing.objects.all()

