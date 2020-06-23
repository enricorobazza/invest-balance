from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.list_assets, name="list_assets"),
    re_path(r'^stock/(?P<code>[-\w.]+)/?$', views.get_stock_price, name='get_stock_price'),
    path('invest', views.make_investment, name="invest")
]
