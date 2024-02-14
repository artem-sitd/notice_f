from django.urls import path
from .views import MessageApi, MailingStat

app_name = "messages"
urlpatterns = [
    path("<int:pk>/", MessageApi.as_view(), name="messages"),
    path("", MessageApi.as_view(), name="messages"),
    path("stat/", MailingStat.as_view(), name="message_stat"),
    path("stat/<int:pk>/", MailingStat.as_view(), name="message_stat_id"),

]
