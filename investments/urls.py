from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.summary, name="summary"),
    re_path(r'^stock/(?P<code>[-\w.]+)/?$', views.get_stock_price, name='get_stock_price'),
    path('dollarquote', views.get_dollar_quote, name="get_dollar_quote"),
    path('invest', views.make_investment, name="invest"),
    path('assets', views.list_assets, name="list_assets"),
    path('assets/add', views.add_asset, name="add_asset"),
    path('category/add', views.add_category, name="add_category"),
    path('transfer/add', views.add_transfer, name="add_transfer"),
    path('saving/add', views.add_saving, name="add_saving"),
    path('history', views.history, name="history"),
    path('history/add', views.add_purchase, name="add_purchase"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
]
