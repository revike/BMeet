from django.urls import path
from channels.routing import URLRouter
from .consumers import BoardConsumer

websockets = URLRouter([
    path(
        "board/<int:board_id>", BoardConsumer.as_asgi(),
    ),
])
