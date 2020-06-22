from django.contrib import admin
from .models import Category, StockExchange, Asset, AssetPurchase, Currency, Transfer

# Register your models here.
admin.site.register(Currency)
admin.site.register(Category)
admin.site.register(StockExchange)
admin.site.register(Asset)
admin.site.register(AssetPurchase)
admin.site.register(Transfer)