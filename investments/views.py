from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Asset, AssetPurchase, Category
from django.db.models import F, FloatField, Sum, Avg
import json
import urllib.request
from forex_python.converter import CurrencyRates

def home(request):
  return HttpResponse('<h1>Home Page</h1>')

# transfer valor inicial / valor final

def list_assets(request):
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

  return JsonResponse({"price": "%.2f"%price})

def make_investment(request):
  assets = Asset.objects.filter(user=request.user)
  categories = Category.objects.filter(user=request.user).aggregate(weight_sum=Sum('weight', output_field=FloatField()))

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

  return render(request, 'MakeInvestment/makeinvestment.html', {'assets': assets})