from django.shortcuts import render
from django.http import JsonResponse
from ..models import AssetPurchase, Asset, Saving, PriceHistory
from django.db.models import F, FloatField, Sum
from django.db.models.functions import ExtractMonth, ExtractYear, Concat, LPad, Cast
from django.db.models.expressions import Window
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from investments.views.services import ServiceViews
import csv
import time
import calendar
import urllib.request
import json
from dateutil.relativedelta import relativedelta
class EvolutionViews():
  def charts(request, code):
    return render(request, 'Charts/stock.html', {"code": code})

  def price_cache(key, start, end):
    url = "https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1mo&events=history&includeAdjustedClose=true"%(key, start, end)

    start = datetime.fromtimestamp(start).replace(day=1).date()
    end = datetime.fromtimestamp(end).replace(day=1).date()

    cache = None
    try:
      cache = PriceHistory.objects.get(start=start, end=end, key=key)
    except PriceHistory.DoesNotExist:
      response = urllib.request.urlopen(url)
      data = list(csv.reader(response.read().decode().splitlines(), delimiter=','))
      json_data = json.dumps(data)
      cache = PriceHistory(data=json_data, key=key, start=start, end=end)
      cache.save()

    return json.loads(cache.data)

  def evolution_chart(request):
    if(request.user.is_anonymous):
      user = User.objects.get(pk=1)
    else:
      user = request.user
      # return redirect('/login')
    assets = list(Asset.objects.filter(user=user).values('code', 'invest_type'))
    first_date = list(AssetPurchase.objects.filter(asset__user=user).order_by('date').values('date'))[0]["date"]

    timestamp_beginning = time.mktime((first_date-timedelta(days=31)).timetuple())

    data = EvolutionViews.price_cache(start=int(timestamp_beginning), end=int(time.time()), key="USDBRL=X")
    usd_prices = [{"date": datetime.date(datetime.strptime(x[0], "%Y-%m-%d")), "value": x[4]} for x in data[1:]]

    last_usd_price = "null"
    index = -1
    while(last_usd_price == "null" and index * -1 < len(usd_prices)):
      last_usd_price = usd_prices[index]["value"]
      index -= 1

    savings = Saving.objects.filter(user=user).values(year = ExtractYear('date'), month=ExtractMonth('date')).annotate(
      accumulated_amount = Window(
        expression=Sum('final_amount'),
        order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
      ),
      accumulated_spend = Window(
        expression=Sum('amount'),
        order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
      ),
    ).order_by('year', 'month').distinct('year', 'month').values('date', 'year', 'month', 'accumulated_amount', 'accumulated_spend', 'final_amount', 'amount')

    for asset in assets:
      print("Getting purchases for %s"%(asset["code"]))
      asset_purchases = AssetPurchase.objects.filter(asset__code=asset["code"], asset__user=user).values(year= ExtractYear('date') ,month=ExtractMonth('date')).annotate(
        accumulated_amount=Window(
          expression=Sum('amount'),
          order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
        ),
        accumulated_spend=Window(
          expression=Sum((F('value')*F('amount')+F('taxes_value'))*F('transfer__value')/F('transfer__final_value')),
          order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
        ),
        spend=Window(
          partition_by = [ExtractYear('date'), ExtractMonth('date')],
          expression=Sum((F('value')*F('amount')+F('taxes_value'))*F('transfer__value')/F('transfer__final_value')),
          order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
        ),
        currency=F('asset__stock_exchange__currency__code')
      ).order_by('year', 'month').distinct('year', 'month').values('date', 'year', 'month', 'accumulated_amount', 'accumulated_spend', 'currency', 'amount', 'spend')

      if(len(asset_purchases) == 0):
        asset.prices = []
        continue

      month_prices = []

      if asset["invest_type"] == 'S':
        data = EvolutionViews.price_cache(start=int(timestamp_beginning), end=int(time.time()), key=asset["code"])
        month_prices = [{"date": datetime.date(datetime.strptime(x[0], "%Y-%m-%d")), "value": x[4]} for x in data[1:]]
      else:
        response = ServiceViews.get_fund_price(request, asset["code"])
        price = json.loads(response.content)['price']
        beginning_date = datetime.fromtimestamp(timestamp_beginning)
        start = beginning_date.month
        end = datetime.now().month
        month_prices = [{"date": (beginning_date+relativedelta(months=x)).date(), "value": price} for x in range(end-start+1)]

      last_price = "null"
      index = -1
      while(last_price == "null" and index * -1 < len(month_prices)):
        last_price = month_prices[index]["value"]
        index -= 1

      index_month = 0

      for month_price in month_prices:
        try:
          month_price["value"] = float(month_price["value"])
        except:
          month_price["value"] = 0.0

        if(index_month >= len(asset_purchases) or asset_purchases[index_month]["date"] > month_price["date"]):
          if(index_month == 0):
            month_price["total_value"] = 0
            month_price["invested_value"] = 0
            month_price["value"] = 0
            month_price["invested"] = 0
            currency = ""
          else:
            month_price["total_value"] = asset_purchases[index_month-1]["accumulated_amount"] * float(month_price["value"])
            month_price["invested_value"] = asset_purchases[index_month-1]["accumulated_spend"]
            month_price["value"] = asset_purchases[index_month-1]["amount"] * float(last_price)
            month_price["invested"] = asset_purchases[index_month-1]["spend"]
            currency = asset_purchases[index_month-1]["currency"]
        else:
          month_price["total_value"] = asset_purchases[index_month]["accumulated_amount"] * month_price["value"]
          month_price["invested_value"] = asset_purchases[index_month]["accumulated_spend"]
          month_price["value"] = asset_purchases[index_month]["amount"] * float(last_price)
          month_price["invested"] = asset_purchases[index_month]["spend"]
          currency = asset_purchases[index_month]["currency"]
          index_month+=1
        
        if(currency == "USD"):
          usd_value = float(usd_prices[index_month]["value"])
          month_price["total_value"] *= usd_value
          month_price["invested"] *= usd_value
          month_price["value"] *= float(last_usd_price)

      asset["prices"] = month_prices  

    months = []
    for i in range(len(assets[0]["prices"])):
      date = assets[0]["prices"][i]["date"]
      month = {"date": date, "total_value": 0, "invested_value": 0, "invested": 0, "value": 0, "components": []}
      for j in range(len(assets)):
        if(i >= len(assets[j]["prices"])):
            break
        month["total_value"] += assets[j]["prices"][i]["total_value"]
        month["invested_value"] += assets[j]["prices"][i]["invested_value"]
        month["invested"] += assets[j]["prices"][i]["invested"]
        month["value"] += assets[j]["prices"][i]["value"]
        month["components"] += [{
          "code": assets[j]["code"],
          "total_value": assets[j]["prices"][i]["total_value"],
          "invested_value": assets[j]["prices"][i]["invested_value"],
          "invested": assets[j]["prices"][i]["invested"],
          "value": assets[j]["prices"][i]["value"],
        }]
      months.append(month)

    index_saving = 0

    for month in months:
      if(index_saving >= len(savings) or savings[index_saving]["date"] > month["date"]):
        if(index_saving > 0):
          month["total_value"] += savings[index_saving-1]["accumulated_amount"]
          month["invested_value"] += savings[index_saving-1]["accumulated_spend"]
          month["invested"] += savings[index_saving-1]["amount"]
          month["value"] += savings[index_saving-1]["final_amount"]
          month["components"] += [{
            "code": "Saving",
            "total_value": savings[index_saving-1]["accumulated_amount"],
            "invested_value": savings[index_saving-1]["accumulated_spend"],
            "invested": savings[index_saving-1]["amount"],
            "value": savings[index_saving-1]["final_amount"],
          }]
      else:
        month["total_value"] += savings[index_saving]["accumulated_amount"]
        month["invested_value"] += savings[index_saving]["accumulated_spend"]
        month["invested"] += savings[index_saving]["amount"]
        month["value"] += savings[index_saving]["final_amount"]
        month["components"] += [{
          "code": "Saving",
          "total_value": savings[index_saving]["accumulated_amount"],
          "invested_value": savings[index_saving]["accumulated_spend"],
          "invested": savings[index_saving]["amount"],
          "value": savings[index_saving]["final_amount"],
        }]
        index_saving += 1
      date = month["date"]
      month["date"] = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
    
    print(months)
    return render(request, 'Charts/evolution.html', {'assets': months })
