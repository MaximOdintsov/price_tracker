import json
import pytest
import websockets
from decimal import Decimal
from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from crypto_project.routing import application
from prices import tasks
from prices.models import Price


class DummyWebSocket:
    def __init__(self, messages):
        self.messages = [json.dumps(m) for m in messages]
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return False
    async def recv(self):
        if not self.messages:
            raise websockets.ConnectionClosedOK(0, "No more messages")
        return self.messages.pop(0)


@pytest.mark.django_db
def test_price_stream(monkeypatch):
    dummy_data = {"c": "50000.0"}
    async def dummy_connect(url):
        return DummyWebSocket([dummy_data])
    monkeypatch.setattr(websockets, "connect", dummy_connect)
    async_to_sync(tasks.price_stream)(symbol="btcusdt", max_messages=1)
    price_obj = Price.objects.get(symbol="BTCUSDT")
    assert price_obj.price == Decimal(dummy_data["c"])


@pytest.mark.django_db
def test_price_history_api(client):
    Price.objects.create(symbol="BTCUSDT", price=Decimal("45000.0"))
    Price.objects.create(symbol="BTCUSDT", price=Decimal("46000.0"))
    response = client.get("/api/prices/?symbol=BTCUSDT")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["symbol"] == "BTCUSDT"
    assert data[0]["price"] == "46000.00000000"
    assert data[1]["price"] == "45000.00000000"


@pytest.mark.asyncio
async def test_websocket_broadcast(settings):
    settings.CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
    communicator = WebsocketCommunicator(application, "/ws/prices/BTCUSDT/")
    connected, _ = await communicator.connect()
    assert connected
    channel_layer = get_channel_layer()
    await channel_layer.group_send("prices_BTCUSDT", {"type": "send_price", "price": "12345.67"})
    response = await communicator.receive_json_from()
    assert response["price"] == "12345.67"
    await communicator.disconnect()
