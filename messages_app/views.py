import logging.config
from config import dict_config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import generics, status
from drf_spectacular.utils import extend_schema
from mailings.models import Mailing
from .models import Messages
from .serializers import MessageSeralizer
from django.db.models import Count, Case, When

logging.config.dictConfig(dict_config)
logger = logging.getLogger(__name__)


class MessageApi(APIView):
    @extend_schema(description='если передать в конец url id - выведет конкретное собщение, если не передать выведет '
                               'все имеющиеся сообщения из базы')
    def get(self, request: Request, **kwargs) -> Response:
        logger.info('вход в get MessageApi')
        message_id = kwargs.get('pk')
        if message_id:
            logger.info(f'get MessageApi передан pk={message_id}')
            message = generics.get_object_or_404(Messages, id=message_id)
            serialized = MessageSeralizer(message, many=False)
            return Response(serialized.data, status=200)
        logger.info('get MessageApi не передан в get MessageApikwargs.get("pk"), выводим весь список')
        message = Messages.objects.all()
        serialized = MessageSeralizer(message, many=True)
        logger.info('get MessageApi отдаем весь перечень сообщений')
        return Response(serialized.data, status=200)


class MailingStat(APIView):
    @extend_schema(description='Подробная инфо по рассылке. в конец URL передать id рассылки, или не передавать - '
                               'тогда выведет общую статистику',
                   responses=MessageSeralizer)
    def get(self, request: Request, **kwargs) -> Response:
        logger.info('вход в get MailingStat')
        mailing_id = kwargs.get('pk')
        if mailing_id:
            logger.info(f'get MailingStat передан pk={mailing_id}')
            filtered_messages = Messages.objects.select_related('mailings').filter(mailings=mailing_id)
            if not filtered_messages:
                logger.info('get MailingStat не найдено сообщение по указанному pk')
                return Response({'error': 'сообщений по указанной рассылке не найдено'},
                                status=status.HTTP_400_BAD_REQUEST)
            # Подсчитываем количество сообщений со статусом True и False
            total_messages = filtered_messages.count()
            true_messages = filtered_messages.filter(status=True).count()
            false_messages = filtered_messages.filter(status=False).count()
            mailing_info = {
                'Всего сообщений:': total_messages,
                'Отправлено:': true_messages,
                'Не отправлено (ошибки)': false_messages
            }
            serialized = MessageSeralizer(filtered_messages, many=True)
            logger.info('get MailingStat возвращаем инфо о сообщении')
            return Response({'mailing_info': mailing_info, 'messages': serialized.data}, status=status.HTTP_200_OK)
        logger.info('get MailingStat не передан kwargs.get(pk), формируем весь перечень рассылок')
        mailings_info = Mailing.objects.annotate(
            total_messages=Count('messages'),
            true_messages=Count(Case(When(messages__status=True, then=1))),
            false_messages=Count(Case(When(messages__status=False, then=1)))
        )

        data = []
        for mailing in mailings_info:
            mailing_data = {
                'id': mailing.id,
                'total_messages': mailing.total_messages,
                'true_messages': mailing.true_messages,
                'false_messages': mailing.false_messages
            }
            data.append(mailing_data)
        logger.info('get MailingStat отдаем все рассылки')
        return Response(data, status=status.HTTP_200_OK)
