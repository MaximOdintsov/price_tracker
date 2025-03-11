import asyncio
import json
from decimal import Decimal
import websockets
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer

running_streams = {}


async def price_stream(symbol: str):
    from prices.models import Price

    url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@ticker"
    channel_layer = get_channel_layer()
    try:
        async with websockets.connect(url) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                price_str = data.get("c") or data.get("p")
                if not price_str:
                    continue
                price_val = Decimal(price_str)
                await sync_to_async(Price.objects.create)(symbol=symbol.upper(), price=price_val)
                await channel_layer.group_send(
                    f"prices_{symbol.upper()}",
                    {
                        "type": "send_price",
                        "price": price_str,
                    }
                )
    except Exception as e:
        print(f"Error in price_stream for {symbol}: {e}")
        running_streams.pop(symbol.upper(), None)


async def start_stream_for_symbol(symbol: str):
    """
    Создание задачи на мониторинг валюты, если она еще не создана
    """
    symbol_upper = symbol.upper()
    if symbol_upper not in running_streams:
        task = asyncio.create_task(price_stream(symbol))
        running_streams[symbol_upper] = task
