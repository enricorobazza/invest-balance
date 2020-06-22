from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.list_assets, name="home"),
    re_path(r'^stock/(?P<code>[-\w.]+)/?$', views.get_stock_price, name='get_stock_price'),
]
