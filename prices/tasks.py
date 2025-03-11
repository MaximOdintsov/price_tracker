import asyncio
import json
from decimal import Decimal
import websockets
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer

# Глобальный словарь для хранения запущенных задач по символу
running_streams = {}


async def price_stream(symbol):
    # Выполняем отложенный импорт модели после инициализации приложений Django
    from prices.models import Price

    url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@ticker"
    channel_layer = get_channel_layer()
    try:
        async with websockets.connect(url) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                # Берем цену из ключа "c" или "p" (последняя цена)
                price_str = data.get("c") or data.get("p")
                if not price_str:
                    continue
                price_val = Decimal(price_str)
                # Сохраняем данные в базе (опционально)
                await sync_to_async(Price.objects.create)(symbol=symbol.upper(), price=price_val)
                # Рассылаем данные в группу, соответствующую символу
                await channel_layer.group_send(
                    f"prices_{symbol.upper()}",
                    {
                        "type": "send_price",
                        "price": price_str,
                    }
                )
    except Exception as e:
        print(f"Error in price_stream for {symbol}: {e}")
        # Если произошла ошибка, удаляем задачу, чтобы при следующем подключении можно было её перезапустить
        running_streams.pop(symbol.upper(), None)


async def start_stream_for_symbol(symbol):
    symbol_upper = symbol.upper()
    # Если задача для этого символа ещё не запущена, создаем её
    if symbol_upper not in running_streams:
        task = asyncio.create_task(price_stream(symbol))
        running_streams[symbol_upper] = task
