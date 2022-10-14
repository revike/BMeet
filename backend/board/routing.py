from django.urls import path
from channels.routing import URLRouter
from .consumers import BoardConsumer
from .middleware import TokenAuthMiddleware

websockets = TokenAuthMiddleware(
    URLRouter([
        path("api/board/<int:board_id>/", BoardConsumer.as_asgi()),
    ])
)
