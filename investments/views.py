from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Asset, AssetPurchase, Category, Saving
from django.db.models import F, FloatField, Sum, Avg
import json
import urllib.request
from forex_python.converter import CurrencyRates

class SavingAsAsset():
  def __init__(self, code, category, have, ideal_percentage):
    self.code = code
    self.category = category
    self.have = have
    self.ideal_percentage = ideal_percentage * 100


def list_assets(request):
  if(request.user.is_anonymous):
    return redirect('/admin')

  assets = Asset.objects.filter(user=request.user)
  for asset in assets:
    asset_purchases = AssetPurchase.objects.filter(asset=asset).aggregate(cost_sum=Sum(F('value')*F('amount')*F('transfer__value')/F('transfer__final_value')+F('taxes_value'), output_field=FloatField()), count=Sum(F('amount'), output_field=FloatField()))

    if(asset_purchases['cost_sum']):
      asset.cost_avg = "%.2f" % (asset_purchases['cost_sum'] / asset_purchases['count'])
      asset.count = asset_purchases['count']
    else:
      asset.cost_avg = 0
      asset.count = 0
      
  return render(request, 'Assets/list_assets.html', {'assets': assets})

def get_stock_price(request, code):
  response = urllib.request.urlopen("https://query1.finance.yahoo.com/v8/finance/chart/%s"%code) 
  data = json.load(response)
  meta = data.get("chart").get("result")[0].get("meta")
  price = meta.get("regularMarketPrice")
  currency = meta.get("currency")

  if(str(currency) == "USD"):
    c = CurrencyRates()
    usd_value = c.convert('USD', 'BRL', 1)
    price = price * usd_value

  return JsonResponse({"code": code, "price": "%.2f"%price})

def make_investment(request):
  if(request.user.is_anonymous):
    return redirect('/admin')

  assets = Asset.objects.filter(user=request.user)
  categories = Category.objects.filter(user=request.user).aggregate(weight_sum=Sum('weight', output_field=FloatField()))
  savings_sum = Saving.objects.filter(user=request.user).aggregate(sum=Sum('final_amount', output_field=FloatField()))
  savings = Saving.objects.filter(user=request.user)

  score_sum_by_category = {}

  for asset in assets:
    asset_purchases = AssetPurchase.objects.filter(asset=asset).aggregate(count=Sum(F('amount'), output_field=FloatField()))

    if(asset.category.pk not in score_sum_by_category):
      score_sum_by_category[asset.category.pk] = asset.score
    else:
      score_sum_by_category[asset.category.pk] += asset.score

    if(asset_purchases['count']):
      asset.count = asset_purchases['count']
    else:
      asset.count = 0
  
  for asset in assets:
    category_weight = asset.category.weight / categories["weight_sum"]
    ideal_percentage = asset.score / score_sum_by_category[asset.category.pk] * category_weight * 100
    asset.ideal_percentage = "%.2f" % ideal_percentage  

  saving_asset = None

  if(len(savings) > 0):
    category_weight = savings[0].category.weight / categories["weight_sum"]
    saving_asset = SavingAsAsset("CAIXA", savings[0].category, savings_sum["sum"], category_weight)

  return render(request, 'MakeInvestment/makeinvestment.html', {'assets': assets, 'saving_asset': saving_asset})


def summary(request):
  if(request.user.is_anonymous):
    return redirect('/admin')
    
  categories = AssetPurchase.objects.values(pk=F('asset__category'), title=F('asset__category__title')).filter(asset__user=request.user).annotate(sum=Sum(F('value')*F('amount')*F('transfer__value')/F('transfer__final_value')+F('taxes_value')))

  ret_categories = {}
  total_sum = 0

  for category in categories:
    total_sum += category["sum"]
    assets = AssetPurchase.objects.values(code=F('asset__code')).filter(asset__category=category["pk"]).annotate(amount=Sum('amount'))
    ret_category = {}
    ret_category["pk"] = category["pk"]
    ret_category["title"] = category["title"]
    ret_category["sum"] = "%.2f" % category["sum"]
    ret_category["assets"] = list(assets.values("code", "amount"))
    ret_categories[category["pk"]] = ret_category
  
  savings = Saving.objects.filter(user=request.user)
  savings_sum = 0
  savings_current_value = 0

  for saving in savings:
    savings_sum += saving.amount
    savings_current_value += saving.final_amount

  savings_return = {}
  savings_return["title"] = savings[0].category.title
  savings_return["sum"] = "%.2f" % savings_sum
  savings_return["current_value"] = "%.2f" % savings_current_value
  savings_return["yield"] = "%.2f" % ((savings_current_value - savings_sum) / savings_sum * 100)

  total_sum += savings_sum

  return render(request, 'Summary/summary.html', {'categories': list(ret_categories.values()), 'total_sum': "%.2f"%total_sum, 'savings': savings_return})