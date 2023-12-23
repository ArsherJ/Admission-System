from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('tupadmin/message/', consumers.ChatConsumer.as_asgi()),
    path('applicant/message/', consumers.ChatConsumer.as_asgi()),
    path('interviewer/message/', consumers.ChatConsumer.as_asgi()),
    path('nurse/message/', consumers.ChatConsumer.as_asgi()),
]