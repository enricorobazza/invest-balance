from django.db import models
from django.contrib.auth.models import User
from django.db.models import constraints
from django.utils import timezone

# Create your models here.
class Currency(models.Model):
  title = models.CharField(max_length=255)
  code = models.CharField(max_length=5)

  class Meta:
    verbose_name_plural = "currencies"

  def __str__(self):
    return self.code

class CategoryType(models.Model):
  type = models.CharField(max_length=255)

  def __str__(self):
    return self.type

class Category(models.Model):
  BOOL_CHOICES = ((True, 'Sim'), (False, 'Não'))

  title = models.CharField(max_length=255)
  weight = models.IntegerField()
  user = models.ForeignKey(User, related_name="category_owner", on_delete=models.CASCADE)
  type = models.ForeignKey(CategoryType, related_name="category_type", on_delete=models.PROTECT, null=True)
  can_invest = models.BooleanField(verbose_name="Can be Invested?", default=True, choices=BOOL_CHOICES)

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
  user = models.ForeignKey(User, related_name="transfer_user", on_delete=models.CASCADE)

  def __str__(self):
    return "%s(%s) -> %s(%s) at (%s)" % (self.value, self.from_currency, self.final_value, self.to_currency, self.date)

class Asset(models.Model):
  BOOL_CHOICES = ((True, 'Sim'), (False, 'Não'))
  TYPE_CHOICES = (('S', 'Ação'), ('F', 'Fundo'))

  stock_exchange =  models.ForeignKey(StockExchange, related_name="asset_stock_exchange", on_delete=models.PROTECT)
  category = models.ForeignKey(Category, related_name="asset_category", on_delete=models.CASCADE)
  name = models.CharField(max_length=255)
  short_code = models.CharField(max_length=15)
  code = models.CharField(max_length=20)
  user = models.ForeignKey(User, related_name="asset_user", on_delete=models.CASCADE)
  score = models.FloatField()
  can_invest = models.BooleanField(verbose_name="Can be Invested?", default=True, choices=BOOL_CHOICES)
  fractioned = models.BooleanField(verbose_name="Can be fractioned?", default=False, choices=BOOL_CHOICES)
  invest_type = models.CharField(max_length=1, verbose_name="Tipo de Investimento", default='S', choices=TYPE_CHOICES)

  def __str__(self):
    return self.short_code

class AssetPurchase(models.Model):
  asset = models.ForeignKey(Asset, related_name="purchased_asset", on_delete=models.CASCADE)
  date = models.DateField(default=timezone.now)
  value = models.FloatField()
  amount = models.FloatField()
  transfer = models.ForeignKey(Transfer, related_name="asset_purchase_transfer", on_delete=models.CASCADE)
  taxes_value = models.FloatField(default=0)

  def __str__(self):
    return "%s (%s)"%(str(self.asset), self.date)

class Bank(models.Model):
  title = models.CharField(max_length=255)

  def __str__(self):
    return self.title

class Saving(models.Model):
  bank = models.ForeignKey(Bank, related_name="saving_bank", on_delete=models.CASCADE)
  amount = models.FloatField()
  final_amount = models.FloatField()
  date = models.DateField(default=timezone.now)
  updated = models.DateTimeField(auto_now=True)
  category = models.ForeignKey(Category, related_name="saving_category", on_delete=models.CASCADE)
  user = models.ForeignKey(User, related_name="saving_user", on_delete=models.CASCADE)

  def __str__(self):
    return "%s (%s) at %s" %(self.amount, str(self.bank), self.date)

class OptionsStrategy(models.Model):
  category = models.ForeignKey(Category, related_name="options_category", on_delete=models.PROTECT)
  user = models.ForeignKey(User, related_name="options_user", on_delete=models.CASCADE)

class GuiaBolsoToken(models.Model):
  user = models.OneToOneField(User, on_delete=models.Case, related_name="guiabolso_token_user")
  token = models.TextField()
  last_updated = models.DateTimeField()
  valid = models.BooleanField(default=True)

  @property
  def last_transaction_date(self):
    transactions = GuiaBolsoTransaction.objects.filter(user=self.user).order_by('-date')
    if len(transactions) > 0:
      return transactions[0].date
    return None


class GuiaBolsoCategory(models.Model):
  code = models.BigIntegerField(unique=True)
  user = models.ForeignKey(User, related_name="guiabolso_category_user", on_delete=models.CASCADE) 
  name = models.CharField(max_length=100)
  type = models.CharField(max_length=100)
  color = models.CharField(max_length=6)
  symbol = models.TextField(null=True, blank=True)
  predictable = models.BooleanField(default=False)

  def __str__(self):
    return self.name

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['user', 'id'], name='guia bolso category unique'),
      models.UniqueConstraint(fields=['user', 'name'], name='guia bolso category  name unique'),
    ]
class GuiaBolsoTransaction(models.Model):
  code = models.BigIntegerField(unique=True)
  user = models.ForeignKey(User, related_name="guiabolso_user", on_delete=models.CASCADE)
  date = models.DateTimeField()
  value = models.FloatField()
  label = models.TextField()
  description = models.TextField()
  category = models.ForeignKey(GuiaBolsoCategory, on_delete=models.CASCADE, related_name="category_transactions")
  exclude_from_variable = models.BooleanField(default=False)

  def __str__(self):
    return self.text

  @property
  def text(self):
    if self.description is not None and self.description != "":
      return self.description
    return self.label


class GuiaBolsoCategoryBudget(models.Model):
  category = models.ForeignKey(GuiaBolsoCategory, related_name="budget", on_delete=models.CASCADE)
  goal = models.FloatField(default=0)
  spent = models.FloatField(default=0)
  month = models.IntegerField()
  year = models.IntegerField()

  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['category', 'month', 'year'], name='category budget unique')
    ]