# chat/urls.py
from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    # 기존 채팅 API
    path("api/", views.chat_api, name="chat_api"),
    # 새로운 히스토리 API
    path("history/", views.chat_history_api, name="chat_history_api"),
]
