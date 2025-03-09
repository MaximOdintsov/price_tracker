Запуск сокета: 
docker compose exec web python -c "import django; django.setup(); import asyncio; from prices import tasks; asyncio.run(tasks.price_stream())"
