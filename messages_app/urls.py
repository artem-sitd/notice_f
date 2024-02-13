from django.urls import path
from .views import MessageApi

app_name = "messages"
urlpatterns = [
    path("<int:pk>/", MessageApi.as_view(), name="messages"),
    path("", MessageApi.as_view(), name="messages"),

]
