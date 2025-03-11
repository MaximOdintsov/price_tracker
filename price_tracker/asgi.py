import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import price_tracker.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_tracker.settings')
django.setup()  # ensure Django is loaded (especially for running in separate ASGI server)

# HTTP-handling приложение Django (на случай обычных запросов)
django_asgi_app = get_asgi_application()

# Комбинированный ASGI-роутер: HTTP запросы обслуживает Django, WebSocket - Channels
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(price_tracker.routing.websocket_urlpatterns)
    ),
})