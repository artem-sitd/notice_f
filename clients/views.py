from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from clients.models import Clients, Tag
from rest_framework import status
from .serializers import TagSerializer, ClientSerializer
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view


class ClientsApi(APIView):
    # создание клиента
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='Создание клиента, обязательные параметры: phone (7 цифр), tag, timezone (Europe/Kaliningrad,'
                               ' Europe/Moscow, Europe/Samara, Asia/Yekaterinburg, Asia/Omsk,'
                               'Asia/Krasnoyarsk, Asia/Irkutsk, Asia/Yakutsk, Asia/Vladivostok, Asia/Magadan,'
                               'Asia/Kamchatka]), mobile_code (три цифры) ')
    def post(self, request: Request, **kwargs) -> Response:
        phone = request.data.get('phone')
        tag = request.data.get('tag')
        timezone = request.data.get('timezone')
        mobile_code = request.data.get('mobile_code')
        # Валидация данных
        if not all([phone, tag, timezone, mobile_code]):
            return Response({'error': 'Не все поля указаны'}, status=status.HTTP_400_BAD_REQUEST)
        tag_instance = Tag.objects.filter(id=tag).only('id').first()
        if tag_instance:
            # Обработка данных и создание объекта Clients
            try:
                serializer = ClientSerializer(data={'phone': phone, 'tag': tag_instance.id, 'timezone': timezone,
                                                    'mobile_code': mobile_code})
                serializer.is_valid(raise_exception=True)
            except ValidationError as ve:
                return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
            client = Clients.objects.create(phone=phone, tag=tag_instance, timezone=timezone, mobile_code=mobile_code)
            client.save()
            new_client = ClientSerializer(client, many=False)
            return Response(new_client.data, status=status.HTTP_201_CREATED)
        return Response({'tag': 'не существующий тэг'}, status=status.HTTP_400_BAD_REQUEST)

    # для получения всех или конкретного клиента
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='Чтобы получить инфо по конкретному клиенту - необходимо в конце URL добавить id '
                               'пользователя, чтобы получить весь перечень клиентов - не передавайте ничего после url')
    def get(self, request: Request, **kwargs) -> Response:
        client_id = kwargs.get('pk')
        if client_id:
            client = generics.get_object_or_404(Clients, id=client_id)
            serialized = ClientSerializer(client, many=False)
            return Response(data=serialized.data, status=200)
        all_clients = Clients.objects.all()
        serialized = ClientSerializer(all_clients, many=True)
        return Response(data=serialized.data, status=200)

    # для удаления клиента {pk}
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='необходимо в url передать id клиента для удаления, удаление происходит без подтверждения')
    def delete(self, request: Request, **kwargs) -> Response:
        client_id = kwargs.get('pk')
        if not client_id:
            return Response({'error': 'Не указан идентификатор клиента'}, status=status.HTTP_400_BAD_REQUEST)
        client = generics.get_object_or_404(Clients, id=client_id)
        client.delete()
        return Response({'success': 'Клиент успешно удален'}, status=status.HTTP_204_NO_CONTENT)

    # для изменения клиента {pk}
    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer},
                   description='Необходимо в конце url передать id редактируемого клиента, в теле запроса передать'
                               ' поля для редактирования')
    def patch(self, request: Request, *args, **kwargs) -> Response:
        client_id = kwargs.get('pk')
        if not client_id:
            return Response({'error': 'Не указан идентификатор клиента'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        client = generics.get_object_or_404(Clients, id=client_id)
        if not data:
            return Response({'error': 'не указаны данные для изменения'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serialized = ClientSerializer(client, data=data, partial=True)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)


# протестирован в Postman
class TagsApi(APIView):
    # создание тэга
    @extend_schema(request=TagSerializer, responses=TagSerializer,
                   description='принимает только поле text')
    def post(self, request: Request, **kwargs) -> Response:
        text = request.data.get('text')
        if text and len(text) > 1:
            data = Tag.objects.create(text=text)
            serialized = TagSerializer(data, many=False)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Не указан текст тэга'}, status=status.HTTP_400_BAD_REQUEST)

    # полученеи списка всех тэгов
    @extend_schema(request=TagSerializer, responses=TagSerializer, description='отдает все тэги')
    def get(self, request: Request) -> Response:
        data = Tag.objects.all()
        serialized = TagSerializer(data, many=True)
        return Response(serialized.data, status=200)

    # для удаления тэга
    @extend_schema(request=TagSerializer, responses=TagSerializer,
                   description='можно передать или поле id или text в теле запроса, в url передавать id не надо,'
                               ' удаление без подтверждения')
    def delete(self, request: Request) -> Response:
        data = request.data
        if 'id' in data:
            tag_id = data['id']
            tag = generics.get_object_or_404(Tag, id=tag_id)
        elif 'text' in data:
            tag_text = data['text']
            tag = generics.get_object_or_404(Tag, text=tag_text)
        else:
            return Response({'error': 'Не указан идентификатор или текст тега'}, status=status.HTTP_400_BAD_REQUEST)
        tag.delete()
        return Response({'success': 'Тег успешно удален'}, status=status.HTTP_204_NO_CONTENT)

    # для изменения тэга {pk}
    @extend_schema(request=TagSerializer, responses=TagSerializer,
                   description='в url надо передать id тэга, в тело запроса поле text')
    def patch(self, request: Request, *args, **kwargs) -> Response:
        data = request.data
        tag_id = kwargs.get('pk')
        if not tag_id:
            return Response({'error': 'Не указан идентификатор тэга'}, status=status.HTTP_400_BAD_REQUEST)
        tag = generics.get_object_or_404(Tag, id=tag_id)

        if 'text' in data:
            if data['text'] != '':
                tag.text = data['text']
                tag.save()
                return Response({'message': 'Тег успешно обновлен'}, status=status.HTTP_200_OK)
            return Response({'error': 'Не указан текст тега для обновления'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Не указан текст тега для обновления'}, status=status.HTTP_400_BAD_REQUEST)
