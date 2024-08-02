import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from pagos.consumers import YourConsumer  # Asegúrate de usar el nombre correcto de tu aplicación

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         path("ws/pago/", YourConsumer.as_asgi()),
    #     ])
    # ),
})
