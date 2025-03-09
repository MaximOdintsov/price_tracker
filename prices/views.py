from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from .models import Price


def price_history(request):
    # Return recent price history as JSON (optional ?symbol= filter)
    symbol = request.GET.get("symbol")
    qs = Price.objects.all()
    if symbol:
        qs = qs.filter(symbol=symbol.upper())
    # Last 24 hours, limit to 100 records
    one_day_ago = timezone.now() - timedelta(days=1)
    qs = qs.filter(timestamp__gte=one_day_ago).order_by("-timestamp")[:100]

    data = []
    for record in qs:
        data.append({
            "symbol": record.symbol,
            "price": str(record.price),
            "timestamp": record.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
    return JsonResponse(data, safe=False)


def index(request):
    return render(request, "prices/index.html")