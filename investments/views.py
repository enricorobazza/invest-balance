from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Asset, AssetPurchase, Category, Saving
from django.db.models import F, FloatField, Sum, Avg
import json
import urllib.request
from forex_python.converter import CurrencyRates
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from investments.forms import UserLoginForm, AssetForm, CategoryForm, AssetPurchaseForm, TransferForm, SavingForm
from datetime import datetime
from django.contrib.auth.models import User


class SavingAsAsset():
  def __init__(self, code, category, have, ideal_percentage):
    self.code = code
    self.category = category
    self.have = have
    self.ideal_percentage = ideal_percentage * 100
    self.fractioned = True

def login(request):
    next = request.GET.get('next')
    if(request.user.is_authenticated):
        return redirect(next or '/')

    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        auth_login(request, user)
        return redirect(next or '/')

    return render(request, 'Accounts/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('/')


def list_assets(request):
  if(request.user.is_anonymous):
    user = User.objects.get(pk=1)
  else:
    user = request.user
    # return redirect('/login')

  assets = Asset.objects.filter(user=user)
  for asset in assets:
    asset_purchases = AssetPurchase.objects.filter(asset=asset).aggregate(cost_sum=Sum((F('value')*F('amount')+F('taxes_value'))*F('transfer__value')/F('transfer__final_value'), output_field=FloatField()), count=Sum(F('amount'), output_field=FloatField()))

    if(asset_purchases['cost_sum']):
      asset.cost_avg = "%.2f" % (asset_purchases['cost_sum'] / asset_purchases['count'])
      asset.count = asset_purchases['count']
    else:
      asset.cost_avg = 0
      asset.count = 0
      
  return render(request, 'Assets/list_assets.html', {'assets': assets})

def get_dollar_quote(request):
  c = CurrencyRates()
  usd_value = c.convert('USD', 'BRL', 1)
  return JsonResponse({"quote": usd_value})

def get_options_price(request, code="BOVA11", option="BOVAU985"):
  response = urllib.request.urlopen("https://opcoes.net.br/listaopcoes/completa?idAcao=%s&cotacoes=true&vencimentos=2020-08-17,2020-09-21,2020-10-19,2020-11-16,2020-12-21,2021-01-18,2022-03-18,2022-07-15"%code)
  data = json.load(response)
  opcoes = data.get("data").get("cotacoesOpcoes")
  for opcao in opcoes:
    if(opcao[0] == option+"_2020"):
      return JsonResponse(opcao, safe=False)
  return JsonResponse(data)

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
    user = User.objects.get(pk=1)
  else:
    user = request.user
    # return redirect('/login')

  assets = Asset.objects.filter(user=user)

  categories = Category.objects.filter(user=user).aggregate(weight_sum=Sum('weight', output_field=FloatField()))

  saving_categories = Saving.objects.values('category', title=F('category__title') ,weight=F('category__weight')).filter(user=user).annotate(final_amount=Sum('final_amount', output_field=FloatField()))

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

  initial_patrimony = 0

  for saving_category in saving_categories:
    initial_patrimony += saving_category["final_amount"]
    saving_category["ideal_percentage"] = saving_category["weight"] / categories["weight_sum"] * 100
    saving_category["fractioned"] = True

  return render(request, 'MakeInvestment/makeinvestment.html', {'assets': assets, 'savings': saving_categories, 'initial_patrimony': initial_patrimony})


def summary(request):
  if(request.user.is_anonymous):
    user = User.objects.get(pk=1)
  else:
    user = request.user
    # return redirect('/login')
    
  categories = AssetPurchase.objects.values(pk=F('asset__category'), title=F('asset__category__title')).filter(asset__user=user).annotate(sum=Sum((F('value')*F('amount')+F('taxes_value'))*F('transfer__value')/F('transfer__final_value')))

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

  saving_categories = Saving.objects.values(title=F('category__title')).filter(user=user).annotate(current_value=Sum('final_amount', output_field=FloatField()), sum=Sum('amount', output_field=FloatField()), yield_rate = (F('current_value') - F('sum'))/F('sum'))

  initial_patrimony = 0

  for saving in saving_categories:
    total_sum += saving["sum"]
    initial_patrimony += saving["current_value"]
    saving["yield"] = "%.2f" % (saving["yield_rate"] * 100)

  return render(request, 'Summary/summary.html', {'categories': list(ret_categories.values()), 'total_sum': "%.2f"%total_sum, 'savings': saving_categories, 'initial_patrimony': initial_patrimony})

def history(request):
  if(request.user.is_anonymous):
    user = User.objects.get(pk=1)
  else:
    user = request.user
    # return redirect('/login')

  purchases = AssetPurchase.objects.values("asset", "date", "amount", paid_value=(F('value')+F('taxes_value')/F('amount'))*F('transfer__value')/F('transfer__final_value'), total_value=(F('value')*F('amount')+F('taxes_value'))*F('transfer__value')/F('transfer__final_value'), code=F("asset__code"), short_code=F("asset__short_code")).filter(asset__user = user).order_by('-date')

  return render(request, 'History/history.html', {'purchases': purchases})

def add_asset(request):
  if request.method == 'POST':
      data = request.POST.copy()
      data['user'] = request.user

      form = AssetForm(request.user, data)

      if form.is_valid():
          asset = form.save()
          return redirect('/assets')
      else:
          print(form.errors)
          return JsonResponse({'success': False, 'errors': form.errors}, safe=False)
  else:
      form = AssetForm(request.user)
      return render(request, 'Assets/add_asset.html', {
          'form': form
      })

def add_category(request):
  if request.method == 'POST':
      data = request.POST.copy()
      data['user'] = request.user
      form = CategoryForm(data)
      if form.is_valid():
          asset = form.save()
          return redirect('/')
      else:
          print(form.errors)
          return JsonResponse({'success': False, 'errors': form.errors}, safe=False)
  else:
      form = CategoryForm()
      return render(request, 'Category/add_category.html', {
          'form': form
      })

def add_purchase(request):
  if request.method == 'POST':
      data = request.POST.copy()
      data['user'] = request.user
      data['date'] = datetime.strptime(
                data['date'], '%d/%m/%Y')
      form = AssetPurchaseForm(request.user, data)
      if form.is_valid():
          asset = form.save()
          return redirect('/history')
      else:
          print(form.errors)
          return JsonResponse({'success': False, 'errors': form.errors}, safe=False)
  else:
      form = AssetPurchaseForm(request.user)
      return render(request, 'History/add_purchase.html', {
          'form': form
      })

def add_transfer(request):
  if request.method == 'POST':
      data = request.POST.copy()
      data['user'] = request.user
      data['date'] = datetime.strptime(
                data['date'], '%d/%m/%Y')
      form = TransferForm(data)
      if form.is_valid():
          asset = form.save()
          return redirect('/')
      else:
          print(form.errors)
          return JsonResponse({'success': False, 'errors': form.errors}, safe=False)
  else:
      form = TransferForm()
      return render(request, 'Transfer/add_transfer.html', {
          'form': form
      })

def add_saving(request):
  if request.method == 'POST':
      data = request.POST.copy()
      data['user'] = request.user
      data['date'] = datetime.strptime(
                data['date'], '%d/%m/%Y')
      form = SavingForm(request.user,data)
      if form.is_valid():
          asset = form.save()
          return redirect('/')
      else:
          print(form.errors)
          return JsonResponse({'success': False, 'errors': form.errors}, safe=False)
  else:
      form = SavingForm(request.user)
      return render(request, 'Saving/add_saving.html', {
          'form': form
      })