from django.urls import re_path
from prices import consumers

websocket_urlpatterns = [
    re_path(r'^ws/prices/(?P<symbol>\w+)/$', consumers.PriceConsumer.as_asgi()),
    re_path(r'^ws/api/prices/(?P<symbol>\w+)/$', consumers.PriceConsumer.as_asgi()),
    re_path(r'^ws/price_history/(?P<symbol>\w+)/$', consumers.PriceConsumer.as_asgi()),
]
