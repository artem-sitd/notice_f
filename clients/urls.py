from django.urls import path
from .views import TagsApi, ClientsApi

app_name = "clients"
urlpatterns = [
    path("tags/", TagsApi.as_view(), name="tags_list"),
    path("tags/<int:pk>/", TagsApi.as_view(), name="tag_detail"),
    path("tags/<str:text>/", TagsApi.as_view(), name="tag_detail_by_text"),
    path('<int:pk>/', ClientsApi.as_view(), name='client_detail_delete_patch'),
    path('', ClientsApi.as_view(), name='clients_post'),
]
