from common.consumers import MicrocontrollerConsumer
from django.urls import path


websocket_urlpatterns = [
    path("microcontroller/", MicrocontrollerConsumer.as_asgi())
]
