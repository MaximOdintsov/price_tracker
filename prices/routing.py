from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/prices/(?P<symbol>\w+)/$', consumers.PriceConsumer.as_asgi()),
]
