from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from .models import Price
from asgiref.sync import async_to_sync
from prices.tasks import start_stream_for_symbol


def price_history(request):
    symbol = request.GET.get("symbol")
    if symbol:
        # Запускаем стрим, если он ещё не запущен
        async_to_sync(start_stream_for_symbol)(symbol)

    qs = Price.objects.all()
    if symbol:
        qs = qs.filter(symbol=symbol.upper())

    # Фильтрация по диапазону времени (начало и конец)
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")

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

    qs = qs.filter(timestamp__gte=start_dt, timestamp__lte=end_dt).order_by("-timestamp")

    # Фильтрация по количеству записей
    limit_param = request.GET.get("limit")
    try:
        limit = int(limit_param)
    except (TypeError, ValueError):
        limit = 300
    qs = qs[:limit]

    data = []
    for record in qs:
        data.append({
            "symbol": record.symbol,
            "price": str(record.price),
            "timestamp": record.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
    return JsonResponse(data, safe=False)


def price_history_page(request):
    return render(request, "prices/price_history.html")


def index(request):
    return render(request, "prices/index.html")