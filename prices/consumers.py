import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from prices import tasks  # Импортируем наши фоновые задачи

class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.symbol = self.scope["url_route"]["kwargs"]["symbol"].upper()
        self.group_name = f"prices_{self.symbol}"
        # Добавляем клиента в группу для выбранной криптовалютной пары
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # Запускаем фоновую задачу для выбранного символа, если её ещё нет
        asyncio.create_task(tasks.start_stream_for_symbol(self.symbol))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_price(self, event):
        price = event["price"]
        await self.send(text_data=json.dumps({"price": price}))
