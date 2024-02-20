import logging.config
from config import dict_config
from rest_framework import status, generics
from rest_framework.request import Request
from rest_framework.response import Response
from clients.models import Clients, Tag
from .models import Mailing
from rest_framework.views import APIView
from .serializers import MailSerializer
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

logging.config.dictConfig(dict_config)
logger = logging.getLogger(__name__)


class MailApi(APIView):

    @extend_schema(request=MailSerializer, responses=MailSerializer,
                   description='принимает поля text, end_time в формате: **%Y-%m-%d %H:%M:%S**, mobile_code для'
                               ' фильтрации клиентов и(или) тэг, filter_type ==1 **(фильтрует по двум параметрам из'
                               ' полных перечней клиентов, объединяет, убирает дубликаты)** или ==2 **(фильтрует '
                               'сначала по мобильному коду, затем по тэгу)**')
    def post(self, request: Request, **kwargs) -> Response:
        logger.info('вход в post MailApi')
        text = request.data.get('text')
        end_time = request.data.get('end_time')
        mobile_code = request.data.get('mobile_code')
        tag = request.data.get('tag')
        filter_type = request.data.get('filter_type')
        start_time = request.data.get('start_time')
        if not all([text, end_time, start_time]):
            logger.info('post MailApi не все поля указаны')
            return Response({'error': 'Не все поля указаны'}, status=status.HTTP_400_BAD_REQUEST)

        # Если переданы оба критерия фильтрации
        if mobile_code is not None and tag is not None:
            tag_instance = Tag.objects.filter(text=tag).first()
            if not tag_instance:
                logger.info('post MailApi тэга нет в базе')
                return Response({'error': 'Такого тэга не существует'},
                                status=status.HTTP_400_BAD_REQUEST)
            if filter_type == '1':
                logger.info('post MailApi выбран тип фильтра 1')
                filtered_clients_tag = Clients.objects.select_related('tag').filter(tag=tag_instance).values_list('id',
                                                                                                                  flat=True)
                filtered_clients_code = Clients.objects.filter(mobile_code=mobile_code).values_list('id', flat=True)
                filtered_clients = (filtered_clients_tag | filtered_clients_code).distinct()
            elif filter_type == '2':
                logger.info('post MailApi выбран тип фильтра 2')
                filtered_clients = Clients.objects.filter(mobile_code=mobile_code, tag=tag_instance).values_list('id',
                                                                                                                 flat=True)
            else:
                logger.info('post MailApi filter_type не передан!')
                return Response({'error': 'Необходимо указать filter_type=1 или 2'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Если передан только мобильный код для фильтрации клиентов
        elif mobile_code:
            logger.info('post MailApi передан только mobile_code')
            filtered_clients = Clients.objects.filter(mobile_code=mobile_code).values_list('id', flat=True)

            # Если передан только тэг для фильтрации клиентов
        elif tag:
            logger.info('post MailApi передан только tag')
            tag_instance = Tag.objects.filter(text=tag).first()
            if not tag_instance:
                logger.info('post MailApi передан только tag - не найден в базе')
                return Response({'error': 'Такого тэга не существует'},
                                status=status.HTTP_400_BAD_REQUEST)
            filtered_clients = Clients.objects.filter(tag=tag_instance.id).values_list('id', flat=True)
        else:
            logger.info('post MailApi не передан ни тэг ни мобильный код')
            return Response({'error': 'Необходимо указать mobile_code и(или) tag'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not filtered_clients.exists():
            logger.info('post MailApi клиенты не найдены по указанным критериям')
            return Response({'error': 'По указанным критериям клиенты не найдены'}, status=status.HTTP_404_NOT_FOUND)
        try:
            logger.info('post MailApi пробуем сериализовать ')
            serialized = MailSerializer(data={'text': text, 'end_time': end_time, 'start_time':start_time, 'clients': filtered_clients},
                                        many=False)
            serialized.is_valid(raise_exception=False)
        except ValidationError as ve:
            logger.error(f'post MailApi не удалось сериализовать {ve.detail}')
            return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        logger.info('post MailApi создаем объект Mailing')
        new_mailing = Mailing.objects.create(text=text, end_time=end_time, start_time=start_time)
        new_mailing.clients.set(filtered_clients)
        new_mailing.save()
        logger.info('post MailApi возвращаем ответ клиенту')
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    # если не указывать id в url - выведет весь имеющийся перечень рассылок из базы
    @extend_schema(request=MailSerializer, responses=MailSerializer,
                   description='можно передать в конец url id рассылки, чтобы получить конкретную, или не передавать '
                               '- тогда выведет полынй перечень')
    def get(self, request: Response, **kwargs) -> Response:
        logger.info('вход в get MailApi')
        mailing_id = kwargs.get('pk')
        if mailing_id:
            logger.info(f'get MailApi передан pk={mailing_id}')
            mailing = generics.get_object_or_404(Mailing, id=mailing_id)
            serialized = MailSerializer(mailing, many=False)
            logger.info(f'get MailApi возвращаем результат передан pk={mailing_id}')
            return Response(serialized.data, status=200)
        logger.info(f'get MailApi не передан pk')
        all_mailing = Mailing.objects.all()
        serialized = MailSerializer(all_mailing, many=True)
        logger.info(f'get MailApi возвращаем весь перечень Mailing не передан pk')
        return Response(serialized.data, status=200)

    # удаление рассылки
    @extend_schema(description='передать в конец url id для удаления без подтверждения')
    def delete(self, request: Request, **kwargs) -> Response:
        logger.info('вход в delete MailApi')
        mailing_id = kwargs.get('pk')
        if not mailing_id:
            logger.info('delete MailApi не передан pk')
            return Response({'error': 'Не указан идентификатор рассылки'}, status=status.HTTP_400_BAD_REQUEST)
        mailing = generics.get_object_or_404(Mailing, id=mailing_id)
        mailing.delete()
        logger.info('delete MailApi удаляем объект, возвращаем результат')
        return Response({'success': f'Рассылка id: {mailing_id} удалена!'}, status=status.HTTP_204_NO_CONTENT)

    # редактирование рассылки
    @extend_schema(request=MailSerializer, responses=MailSerializer,
                   description='передать в конец url id для редактирования')
    def patch(self, request: Request, *args, **kwargs) -> Response:
        logger.info('вход в patch MailApi')
        mailing_id = kwargs.get('pk')
        if not mailing_id:
            logger.info('patch MailApi не передан pk')
            return Response({'error': 'Не указан идентификатор рассылки'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data

        mailing = generics.get_object_or_404(Mailing, id=mailing_id)
        if mailing and mailing.status == 'archived':
            logger.info('patch MailApi указанный объект заархивирован, возвращаем ответ')
            return Response({'error': 'рассылка архивирована!'}, status=status.HTTP_400_BAD_REQUEST)

        if not data:
            logger.info('patch MailApi пустые поля для изменения')
            return Response({'error': 'не указаны данные для изменения'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            logger.info('patch MailApi пробуем сериализовать')
            serialized = MailSerializer(mailing, data=data, partial=True)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            logger.info('patch MailApi возвращаем ответ после сериализации')
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            logger.error(f'patch MailApi ошибка валидации в сериализаторе {ve.detail}')
            return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
