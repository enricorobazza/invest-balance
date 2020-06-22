from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Asset
import json
import urllib.request
from forex_python.converter import CurrencyRates

def home(request):
  return HttpResponse('<h1>Home Page</h1>')

def list_assets(request):
  assets = Asset.objects.filter(user=request.user)
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