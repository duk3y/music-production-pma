# mysite/routing.py
from django.urls import path
from mysite.consumers import ChatConsumer  # Adjust myapp to your app name

websocket_urlpatterns = [
    path('ws/chat/<int:project_id>/', ChatConsumer.as_asgi()),
]
