import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import trades.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_project.settings')
django.setup()  # ensure Django is loaded (especially for running in separate ASGI server)

# HTTP-handling приложение Django (на случай обычных запросов)
django_asgi_app = get_asgi_application()

# Комбинированный ASGI-роутер: HTTP запросы обслуживает Django, WebSocket - Channels
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(trades.routing.websocket_urlpatterns)
    ),
})