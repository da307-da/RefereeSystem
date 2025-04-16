from django.urls import re_path
from accounts.fan_chat import FanChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/fan_chat/$', FanChatConsumer.as_asgi()),
]
