import logging.config
from config import dict_config
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from clients.models import Clients, Tag
from rest_framework import status
from .serializers import TagSerializer, ClientSerializer
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

logging.config.dictConfig(dict_config)
logger = logging.getLogger(__name__)


class ClientsApi(APIView):
    # создание клиента
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='Создание клиента, обязательные параметры: phone (7 цифр), tag, timezone (Europe/Kaliningrad,'
                               ' Europe/Moscow, Europe/Samara, Asia/Yekaterinburg, Asia/Omsk,'
                               'Asia/Krasnoyarsk, Asia/Irkutsk, Asia/Yakutsk, Asia/Vladivostok, Asia/Magadan,'
                               'Asia/Kamchatka]), mobile_code (три цифры) ')
    def post(self, request: Request, **kwargs) -> Response:
        logger.info('Вход в post ClientsApi')
        phone = request.data.get('phone')
        tag = request.data.get('tag')
        timezone = request.data.get('timezone')
        mobile_code = request.data.get('mobile_code')
        # Валидация данных
        if not all([phone, tag, timezone, mobile_code]):
            logger.info('post ClientsApi не все поля заполнены')
            return Response({'error': 'Не все поля указаны'}, status=status.HTTP_400_BAD_REQUEST)
        tag_instance = Tag.objects.filter(id=tag).only('id').first()
        if tag_instance:
            # Обработка данных и создание объекта Clients
            logger.info('post ClientsApi найден tag_instance')
            try:
                logger.info('post ClientsApi пробуем сериализовать')
                serializer = ClientSerializer(data={'phone': phone, 'tag': tag_instance.id, 'timezone': timezone,
                                                    'mobile_code': mobile_code})
                serializer.is_valid(raise_exception=True)
            except ValidationError as ve:
                logger.error(f'post ClientsApi {ve.detail}')
                return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
            logger.info('post ClientsApi создаем объект Clients')
            client = Clients.objects.create(phone=phone, tag=tag_instance, timezone=timezone, mobile_code=mobile_code)
            client.save()
            new_client = ClientSerializer(client, many=False)
            logger.info('post ClientsApi создали объект Clients, возвращаем ответ')
            return Response(new_client.data, status=status.HTTP_201_CREATED)
        logger.info('post ClientsApi такого тэга в базе нет')
        return Response({'tag': 'не существующий тэг'}, status=status.HTTP_400_BAD_REQUEST)

    # для получения всех или конкретного клиента
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='Чтобы получить инфо по конкретному клиенту - необходимо в конце URL добавить id '
                               'пользователя, чтобы получить весь перечень клиентов - не передавайте ничего после url')
    def get(self, request: Request, **kwargs) -> Response:
        logger.info('Вход в get ClientsApi')
        client_id = kwargs.get('pk')
        if client_id:
            logger.info(f'get ClientsApi передан pk={client_id}')
            client = generics.get_object_or_404(Clients, id=client_id)
            serialized = ClientSerializer(client, many=False)
            logger.info(f'get ClientsApi возвращаем клиента передан pk={client_id}')
            return Response(data=serialized.data, status=200)
        logger.info(f'get ClientsApi не передан pk')
        all_clients = Clients.objects.all()
        serialized = ClientSerializer(all_clients, many=True)
        logger.info(f'get ClientsApi сериализовали, передаем весь список клиентов')
        return Response(data=serialized.data, status=200)

    # для удаления клиента {pk}
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='необходимо в url передать id клиента для удаления, удаление происходит без подтверждения')
    def delete(self, request: Request, **kwargs) -> Response:
        logger.info('Вход в delete ClientsApi')
        client_id = kwargs.get('pk')
        if not client_id:
            logger.info('delete ClientsApi не передан рк')
            return Response({'error': 'Не указан идентификатор клиента'}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f'delete ClientsApi передан рк={client_id}')
        client = generics.get_object_or_404(Clients, id=client_id)
        client.delete()
        logger.info(f'delete ClientsApi удаляем объект clients, возвращаем ответ')
        return Response({'success': 'Клиент успешно удален'}, status=status.HTTP_204_NO_CONTENT)

    # для изменения клиента {pk}
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='Необходимо в конце url передать id редактируемого клиента, в теле запроса передать'
                               ' поля для редактирования')
    def patch(self, request: Request, *args, **kwargs) -> Response:
        logger.info('вход в patch ClientsApi')
        client_id = kwargs.get('pk')
        if not client_id:
            logger.info('patch ClientsApi не передан client_id')
            return Response({'error': 'Не указан идентификатор клиента'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        client = generics.get_object_or_404(Clients, id=client_id)
        if not data:
            logger.info('patch ClientsApi не указаны поля для изменения')
            return Response({'error': 'не указаны данные для изменения'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            logger.info('patch ClientsApi пробуем сериализовать')
            serialized = ClientSerializer(client, data=data, partial=True)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            logger.info('patch ClientsApi сериализовали, возвращаем ответ')
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            logger.error(f'patch ClientsApi jib,rf cthbfkbpfwbb {ve.detail}')
            return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)


# протестирован в Postman
class TagsApi(APIView):
    # создание тэга
    @extend_schema(request=TagSerializer, responses=TagSerializer,
                   description='принимает только поле text')
    def post(self, request: Request, **kwargs) -> Response:
        logger.info('вход в post TagsApi')
        text = request.data.get('text')
        if text and len(text) > 1:
            logger.info('post TagsApi сериализуем, создаем тэг')
            data = Tag.objects.create(text=text)
            serialized = TagSerializer(data, many=False)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        logger.info('post TagsApi не передано поле text')
        return Response({'error': 'Не указан текст тэга'}, status=status.HTTP_400_BAD_REQUEST)

    # полученеи списка всех тэгов
    @extend_schema(request=TagSerializer, responses=TagSerializer, description='отдает все тэги')
    def get(self, request: Request) -> Response:
        logger.info('вход в get TagsApi')
        data = Tag.objects.all()
        serialized = TagSerializer(data, many=True)
        logger.info('get TagsApi сериализовали, отдаем все тэги')
        return Response(serialized.data, status=200)

    # для удаления тэга
    @extend_schema(request=TagSerializer, responses=TagSerializer,
                   description='можно передать или поле id или text в теле запроса, в url передавать id не надо,'
                               ' удаление без подтверждения')
    def delete(self, request: Request) -> Response:
        logger.info('вход в delete TagsApi')
        data = request.data
        if 'id' in data:
            logger.info('delete TagsApi передано поле id')
            tag_id = data['id']
            tag = generics.get_object_or_404(Tag, id=tag_id)
        elif 'text' in data:
            logger.info('delete TagsApi передано поле text')
            tag_text = data['text']
            tag = generics.get_object_or_404(Tag, text=tag_text)
        else:
            logger.info('delete TagsApi не передано ни поле text, ни поле id')
            return Response({'error': 'Не указан идентификатор или текст тега'}, status=status.HTTP_400_BAD_REQUEST)
        logger.info('delete TagsApi объект tag удален')
        tag.delete()
        return Response({'success': 'Тег успешно удален'}, status=status.HTTP_204_NO_CONTENT)

    # для изменения тэга {pk}
    @extend_schema(request=TagSerializer, responses=TagSerializer,
                   description='в url надо передать id тэга, в тело запроса поле text')
    def patch(self, request: Request, *args, **kwargs) -> Response:
        logger.info('вход в patch TagsApi')
        data = request.data
        tag_id = kwargs.get('pk')
        if not tag_id:
            logger.info('patch TagsApi не указан в url pk')
            return Response({'error': 'Не указан идентификатор тэга'}, status=status.HTTP_400_BAD_REQUEST)
        tag = generics.get_object_or_404(Tag, id=tag_id)

        if 'text' in data:
            if data['text'] != '':
                tag.text = data['text']
                tag.save()
                return Response({'message': 'Тег успешно обновлен'}, status=status.HTTP_200_OK)
            logger.info('patch TagsApi поле text пустое')
            return Response({'error': 'Не указан текст тега для обновления'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info('patch TagsApi не передано поле text')
            return Response({'error': 'Не указан текст тега для обновления'}, status=status.HTTP_400_BAD_REQUEST)
