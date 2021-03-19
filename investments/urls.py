from django.urls import path, re_path
from .views.auth import AuthViews
from .views.assets import AssetsViews
from .views.summary import SummaryViews
from .views.services import ServiceViews
from .views.evolution import EvolutionViews
from .views.invest import InvestViews
from .views.history import HistoryViews

urlpatterns = [
    path('', SummaryViews.summary, name="summary"),
    re_path(r'^stock/(?P<code>[-\w.]+)/?$', ServiceViews.get_stock_price, name='get_stock_price'),
    re_path(r'^fund/(?P<code>[-\w.]+)/?$', ServiceViews.get_fund_price, name='get_fund_price'),
    re_path(r'^dividends/(?P<code>[-\w.]+)/?$', ServiceViews.get_stock_dividends, name='get_stock_dividends'),
    re_path(r'^history/(?P<code>[-\w.]+)/?$', ServiceViews.get_stock_historical_price, name='get_stock_historical_price'),
    re_path(r'^option/(?P<code>[-\w.]+)/(?P<option>[-\w.]+)/?$', ServiceViews.get_options_price, name='get_options_price'),
    path('dollarquote', ServiceViews.get_dollar_quote, name="get_dollar_quote"),
    path('invest', InvestViews.make_investment, name="invest"),
    path('assets', AssetsViews.list_assets, name="list_assets"),
    path('evolution', EvolutionViews.evolution_chart, name="evolution"),
    re_path(r'^charts/(?P<code>[-\w.]+)/?$', EvolutionViews.charts, name='charts'),
    path('assets/add', AssetsViews.add_asset, name="add_asset"),
    path('category/add', SummaryViews.add_category, name="add_category"),
    path('transfer/add', HistoryViews.add_transfer, name="add_transfer"),
    path('saving/add', HistoryViews.add_saving, name="add_saving"),
    path('history', HistoryViews.history, name="history"),
    path('history/add', HistoryViews.add_purchase, name="add_purchase"),
    path('login', AuthViews.login, name="login"),
    path('logout', AuthViews.logout, name="logout"),
]
