from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    # re_path(r"ws/comments/(?P<slug>\w+)/$", consumers.CommentConsumer.as_asgi()),
    path("ws/comments/<slug:slug>", consumers.CommentConsumer.as_asgi()),
]