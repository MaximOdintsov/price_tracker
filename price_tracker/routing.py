import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import prices.routing


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "price_tracker.settings")
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(prices.routing.websocket_urlpatterns)
    ),
})
