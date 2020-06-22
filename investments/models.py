from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Currency(models.Model):
  title = models.CharField(max_length=255)
  code = models.CharField(max_length=5)

  class Meta:
    verbose_name_plural = "currencies"

  def __str__(self):
    return self.code

class Category(models.Model):
  title = models.CharField(max_length=255)
  weight = models.IntegerField()
  user = models.ForeignKey(User, related_name="category_owner", on_delete=models.CASCADE)

  class Meta:
    verbose_name_plural = "categories"

  def __str__(self):
    return self.title

class StockExchange(models.Model):
  name = models.CharField(max_length=255)
  currency = models.ForeignKey(Currency, related_name="stock_exchange_currency", on_delete=models.PROTECT)

  def __str__(self):
    return self.name

class Transfer(models.Model):
  from_currency = models.ForeignKey(Currency, related_name="from_currency", on_delete=models.PROTECT)
  to_currency = models.ForeignKey(Currency, related_name="to_currency", on_delete=models.PROTECT)
  value = models.FloatField()
  final_value = models.FloatField()
  date = models.DateField(default=timezone.now)

  def __str__(self):
    return "%s(%s) -> %s(%s) at (%s)" % (self.value, self.from_currency, self.final_value, self.to_currency, self.date)

class Asset(models.Model):
  stock_exchange =  models.ForeignKey(StockExchange, related_name="asset_stock_exchange", on_delete=models.PROTECT)
  category = models.ForeignKey(Category, related_name="asset_category", on_delete=models.PROTECT)
  name = models.CharField(max_length=255)
  short_code = models.CharField(max_length=15)
  code = models.CharField(max_length=20)
  user = models.ForeignKey(User, related_name="asset_user", on_delete=models.CASCADE)
  score = models.FloatField()

  def __str__(self):
    return self.name

class AssetPurchase(models.Model):
  asset = models.ForeignKey(Asset, related_name="purchased_asset", on_delete=models.PROTECT)
  date = models.DateField(default=timezone.now)
  value = models.FloatField()
  amount = models.IntegerField()
  transfer = models.ForeignKey(Transfer, related_name="asset_purchase_transfer", on_delete=models.PROTECT)

  def __str__(self):
    return self.asset
