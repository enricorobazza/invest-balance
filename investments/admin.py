from django.contrib import admin
from .models import Category, StockExchange, Asset, AssetPurchase, Currency, Transfer, Bank, Saving, CategoryType, GuiaBolsoTransaction
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class AssetPurchaseResource(resources.ModelResource):
	class Meta:
		model = AssetPurchase
		fields = ('asset__user', 'asset__name', 'date', 'value', 'amount', 'transfer__from_currency', 'transfer__to_currency', 'transfer__value', 'transfer__final_value', 'taxes_value')

class AssetPurchaseAdmin(ImportExportModelAdmin):
    resource_class = AssetPurchaseResource

class AssetAdmin(admin.ModelAdmin):
	list_display = ('name', 'user')	
	list_filter = ('user', )

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'user')	
	list_filter = ('user', )

class GuiaBolsoTransactionAdmin(admin.ModelAdmin):
	list_display = ('user', 'date', 'value', 'label', 'description', 'category')
	list_filter = ('user', 'date', 'category')

# Register your models here.
admin.site.register(Currency)
admin.site.register(Category, CategoryAdmin)
admin.site.register(StockExchange)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetPurchase, AssetPurchaseAdmin)
admin.site.register(Transfer)
admin.site.register(Bank)
admin.site.register(Saving)
admin.site.register(CategoryType)
admin.site.register(GuiaBolsoTransaction, GuiaBolsoTransactionAdmin)