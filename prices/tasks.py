import asyncio
import json
from decimal import Decimal
import websockets
from asgiref.sync import sync_to_async
from .models import Price


async def price_stream(symbol="btcusdt", max_messages=None):
    # Connect to Binance WebSocket and continuously stream prices.
    # Save each price to DB and broadcast to WebSocket clients.
    symbol = symbol.lower()
    url = f"wss://stream.binance.com:9443/ws/{symbol}@ticker"
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    try:
        async with websockets.connect(url) as ws:
            count = 0
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                price_str = data.get("c") or data.get("p")
                if not price_str:
                    continue
                price_val = Decimal(price_str)
                await sync_to_async(Price.objects.create)(symbol=symbol.upper(), price=price_val)
                if channel_layer:
                    group = f"prices_{symbol}"
                    await channel_layer.group_send(group, {
                        "type": "send_price",
                        "price": price_str
                    })
                if max_messages:
                    count += 1
                    if count >= max_messages:
                        break
    except Exception as e:
        print(f"Error in price_stream: {e}")
