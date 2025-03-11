from django.contrib import admin
from django.urls import path
from prices import views

urlpatterns = [
    path('', views.index, name='index'),
    path("admin/", admin.site.urls),
    path("api/prices/", views.price_history, name="price_history"),
    path("price_history/", views.price_history_page, name="price_history_page"),
]
