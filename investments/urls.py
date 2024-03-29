from django.urls import path, re_path, include
from .views.auth import AuthViews
from .views.assets import AssetsViews
from .views.summary import SummaryViews
from .views.services import ServiceViews
from .views.evolution import EvolutionViews
from .views.invest import InvestViews
from .views.history import HistoryViews
from .views.risk import RiskViews
from .views.guiabolso import GuiaBolsoViews
from .api.guiabolso import GuiaBolsoTokenViewSet

from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'guiabolso', GuiaBolsoTokenViewSet, basename="GuiaBolsoToken")

urlpatterns = [
    path('', SummaryViews.summary, name="summary"),

    path('api/', include(router.urls + [
        re_path(r'^token/?$', jwt_views.TokenObtainPairView.as_view(),
                name='token_obtain_pair'),
        re_path(r'^token/refresh/?$',
                jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    ])),

    re_path(r'^stock/(?P<code>[-\w.]+)/?$', ServiceViews.get_stock_price, name='get_stock_price'),
    re_path(r'^fund/(?P<code>[-\w.]+)/?$', ServiceViews.get_fund_price, name='get_fund_price'),
    path('history/add', HistoryViews.add_purchase, name="add_purchase"),
    path('history', HistoryViews.history, name="history"),
    re_path(r'^dividends/(?P<code>[-\w.]+)/?$', ServiceViews.get_stock_dividends, name='get_stock_dividends'),
    re_path(r'^history/(?P<code>[-\w.]+)/?$', ServiceViews.get_stock_historical_price, name='get_stock_historical_price'),
    re_path(r'^option/(?P<code>[-\w.]+)/(?P<option>[-\w.]+)/?$', ServiceViews.get_options_price, name='get_options_price'),
    path('dollarquote', ServiceViews.get_dollar_quote, name="get_dollar_quote"),
    path('invest', InvestViews.make_investment, name="invest"),
    path('assets', AssetsViews.list_assets, name="list_assets"),
    path('evolution', EvolutionViews.evolution_chart, name="evolution"),
    path('risk', RiskViews.efficient_frontier, name='risk'),
    path('risk/<int:category>', RiskViews.efficient_frontier, name='risk_category'),
    re_path(r'^charts/(?P<code>[-\w.]+)/?$', EvolutionViews.charts, name='charts'),
    path('assets/add', AssetsViews.add_asset, name="add_asset"),
    path('assets/split', AssetsViews.split, name="split_asset"),
    path('category/add', SummaryViews.add_category, name="add_category"),
    path('transfer/add', HistoryViews.add_transfer, name="add_transfer"),
    path('guiabolso/token', GuiaBolsoViews.add_token, name="add_token"),
    path('guiabolso/refresh', GuiaBolsoViews.refresh_transactions, name="refresh_guiabolso"),
    path('guiabolso', GuiaBolsoViews.list_transactions, name="list_guiabolso"),
    path('saving/add', HistoryViews.add_saving, name="add_saving"),
    path('login', AuthViews.login, name="login"),
    path('logout', AuthViews.logout, name="logout"),
]
