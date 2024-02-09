from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Mailing
from rest_framework.views import APIView


class MailApi(APIView):

    def post(self, request: Request, **kwargs) -> Response:

        pass

    def get(self, request: Response, **kwargs) -> Response:
        pass

    def delete(self, request: Request, **kwargs) -> Response:
        pass

    def patch(self, request: Request, *args, **kwargs) -> Response:
        pass
