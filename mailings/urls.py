from django.urls import path
from .views import MailApi

app_name = "mailings"
urlpatterns = [
    path("", MailApi.as_view(), name="mailings_post"),
    path('<int:pk>/', MailApi.as_view(), name="mailings_get"),

]
