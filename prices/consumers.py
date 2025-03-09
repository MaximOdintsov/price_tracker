import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        symbol = self.scope["url_route"]["kwargs"].get("symbol").lower()  # Приводим к нижнему регистру
        self.group_name = f"prices_{symbol}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # No client messages are expected in this consumer
        pass

    async def send_price(self, event):
        price = event["price"]
        await self.send(text_data=json.dumps({"price": price}))
