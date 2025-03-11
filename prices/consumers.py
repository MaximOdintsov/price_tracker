import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import timedelta
from asgiref.sync import sync_to_async
from prices.tasks import start_stream_for_symbol  # импортируем функцию запуска стриминга


class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.symbol = self.scope['url_route']['kwargs']['symbol'].upper()
        self.group_name = f"prices_{self.symbol}"
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Запускаем стриминг для выбранного символа
        await start_stream_for_symbol(self.symbol)

        # Если в query-параметрах есть данные для истории, сразу отправляем их
        query_string = self.scope['query_string'].decode('utf-8')
        from urllib.parse import parse_qs
        qs_params = parse_qs(query_string)
        start_param = qs_params.get("start", [None])[0]
        end_param = qs_params.get("end", [None])[0]
        limit_param = qs_params.get("limit", [300])[0]

        if start_param or end_param:
            if start_param:
                start_dt = parse_datetime(start_param)
                if not start_dt:
                    start_dt = timezone.now() - timedelta(days=1)
                else:
                    if timezone.is_naive(start_dt):
                        start_dt = timezone.make_aware(start_dt)
            else:
                start_dt = timezone.now() - timedelta(days=1)

            if end_param:
                end_dt = parse_datetime(end_param)
                if not end_dt:
                    end_dt = timezone.now()
                else:
                    if timezone.is_naive(end_dt):
                        end_dt = timezone.make_aware(end_dt)
            else:
                end_dt = timezone.now()

            try:
                limit = int(limit_param)
            except:
                limit = 300

            @sync_to_async
            def fetch_history():
                from prices.models import Price
                qs = Price.objects.filter(symbol=self.symbol, timestamp__gte=start_dt, timestamp__lte=end_dt).order_by(
                    "-timestamp")[:limit]
                data = []
                for record in qs:
                    data.append({
                        "symbol": record.symbol,
                        "price": str(record.price),
                        "timestamp": record.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                    })
                return data

            history_data = await fetch_history()
            await self.send(text_data=json.dumps({"history": history_data}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Обработка входящих сообщений, если нужно
        pass

    async def send_price(self, event):
        price = event["price"]
        await self.send(text_data=json.dumps({"price": price}))
