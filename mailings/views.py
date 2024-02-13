from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.request import Request
from rest_framework.response import Response
from clients.models import Clients, Tag
from .models import Mailing
from rest_framework.views import APIView
from .serializers import MailSerializer
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema


class MailApi(APIView):

    @extend_schema(request=MailSerializer, responses=MailSerializer,
                   description='принимает поля text, end_time в формате: **%Y-%m-%d %H:%M:%S**, mobile_code для'
                               ' фильтрации клиентов и(или) тэг, filter_type ==1 **(фильтрует по двум параметрам из'
                               ' полных перечней клиентов, объединяет, убирает дубликаты)** или ==2 **(фильтрует '
                               'сначала по мобильному коду, затем по тэгу)**')
    def post(self, request: Request, **kwargs) -> Response:
        text = request.data.get('text')
        end_time = request.data.get('end_time')
        mobile_code = request.data.get('mobile_code')
        tag = request.data.get('tag')
        filter_type = request.data.get('filter_type')
        if not all([text, end_time]):
            return Response({'error': 'Не все поля указаны'}, status=status.HTTP_400_BAD_REQUEST)

        # Если переданы оба критерия фильтрации
        if mobile_code is not None and tag is not None:
            tag_instance = Tag.objects.filter(text=tag).first()
            if not tag_instance:
                return Response({'error': 'Такого тэга не существует'},
                                status=status.HTTP_400_BAD_REQUEST)
            if filter_type == '1':
                filtered_clients_tag = Clients.objects.select_related('tag').filter(tag=tag_instance).values_list('id',
                                                                                                                  flat=True)
                filtered_clients_code = Clients.objects.filter(mobile_code=mobile_code).values_list('id', flat=True)
                filtered_clients = (filtered_clients_tag | filtered_clients_code).distinct()
            elif filter_type == '2':
                filtered_clients = Clients.objects.filter(mobile_code=mobile_code, tag=tag_instance).values_list('id',
                                                                                                                 flat=True)
            else:
                return Response({'error': 'Необходимо указать filter_type=1 или 2'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Если передан только мобильный код для фильтрации клиентов
        elif mobile_code:
            filtered_clients = Clients.objects.filter(mobile_code=mobile_code).values_list('id', flat=True)

            # Если передан только тэг для фильтрации клиентов
        elif tag:
            tag_instance = Tag.objects.filter(text=tag).first()
            if not tag_instance:
                return Response({'error': 'Такого тэга не существует'},
                                status=status.HTTP_400_BAD_REQUEST)
            filtered_clients = Clients.objects.filter(tag=tag_instance.id).values_list('id', flat=True)
        else:
            return Response({'error': 'Необходимо указать mobile_code и(или) tag'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not filtered_clients.exists():
            return Response({'error': 'По указанным критериям клиенты не найдены'}, status=status.HTTP_404_NOT_FOUND)
        try:
            serialized = MailSerializer(data={'text': text, 'end_time': end_time, 'clients': filtered_clients},
                                        many=False)
            serialized.is_valid(raise_exception=True)
        except ValidationError as ve:
            return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        new_mailing = Mailing.objects.create(text=text, end_time=end_time)
        new_mailing.clients.set(filtered_clients)
        new_mailing.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    # если не указывать id в url - выведет весь имеющийся перечень рассылок из базы
    @extend_schema(request=MailSerializer, responses=MailSerializer,
                   description='можно передать в конец url id рассылки, чтобы получить конкретную, или не передавать '
                               '- тогда выведет полынй перечень')
    def get(self, request: Response, **kwargs) -> Response:
        mailing_id = kwargs.get('pk')
        if mailing_id:
            mailing = generics.get_object_or_404(Mailing, id=mailing_id)
            serialized = MailSerializer(mailing, many=False)
            return Response(serialized.data, status=200)
        all_mailing = Mailing.objects.all()
        serialized = MailSerializer(all_mailing, many=True)
        return Response(serialized.data, status=200)

    # удаление рассылки
    @extend_schema(description='передать в конец url id для удаления без подтверждения')
    def delete(self, request: Request, **kwargs) -> Response:
        mailing_id = kwargs.get('pk')
        if not mailing_id:
            return Response({'error': 'Не указан идентификатор рассылки'}, status=status.HTTP_400_BAD_REQUEST)
        mailing = generics.get_object_or_404(Mailing, id=mailing_id)
        mailing.delete()
        return Response({'success': f'Рассылка id: {mailing_id} удалена!'}, status=status.HTTP_204_NO_CONTENT)

    # редактирование рассылки
    @extend_schema(request=MailSerializer, responses=MailSerializer,
                   description='передать в конец url id для редактирования')
    def patch(self, request: Request, *args, **kwargs) -> Response:
        mailing_id = kwargs.get('pk')
        if not mailing_id:
            return Response({'error': 'Не указан идентификатор рассылки'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data

        # убираем created_at, чтобы не менять в базе, если указано в запросе
        check_created = data.get('created_at')
        if check_created:
            data.pop('created_at')

        mailing = generics.get_object_or_404(Mailing, id=mailing_id)
        if not data:
            return Response({'error': 'не указаны данные для изменения'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serialized = MailSerializer(mailing, data=data, partial=True)
            serialized.is_valid(raise_exception=True)
            serialized.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
