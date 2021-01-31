from django.shortcuts import render
from django.http import JsonResponse
from ..models import AssetPurchase, Asset, Saving
from django.db.models import F, FloatField, Sum
from django.db.models.functions import ExtractMonth, ExtractYear, Concat, LPad, Cast
from django.db.models.expressions import Window
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import csv
import time
import calendar
import urllib.request

class EvolutionViews():
  def charts(request, code):
    return render(request, 'Charts/stock.html', {"code": code})

  def evolution_chart(request):
    if(request.user.is_anonymous):
      user = User.objects.get(pk=1)
    else:
      user = request.user
      # return redirect('/login')
    assets = list(Asset.objects.filter(user=user).values('code'))
    first_date = list(AssetPurchase.objects.filter(asset__user=user).order_by('date').values('date'))[0]["date"]

    timestamp_beginning = time.mktime((first_date-timedelta(days=31)).timetuple())

    response = urllib.request.urlopen("https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1mo&events=history&includeAdjustedClose=true"%("USDBRL=X", int(timestamp_beginning), int(time.time())))

    usd_prices = [{"date": datetime.date(datetime.strptime(x[0], "%Y-%m-%d")), "value": x[4]} for x in list(csv.reader(response.read().decode().splitlines(), delimiter=','))[1:]]

    savings = Saving.objects.filter(user=user).values(year = ExtractYear('date'), month=ExtractMonth('date')).annotate(
      accumulated_amount = Window(
        expression=Sum('final_amount'),
        order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
      ),
      accumulated_spend = Window(
        expression=Sum('amount'),
        order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
      )
    ).order_by('year', 'month').distinct('year', 'month').values('date', 'year', 'month', 'accumulated_amount', 'accumulated_spend')

    for asset in assets:
      asset_purchases = AssetPurchase.objects.filter(asset__code=asset["code"], asset__user=user).values(year= ExtractYear('date') ,month=ExtractMonth('date')).annotate(
        accumulated_amount=Window(
          expression=Sum('amount'),
          order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
        ),
        accumulated_spend=Window(
          expression=Sum((F('value')*F('amount')+F('taxes_value'))*F('transfer__value')/F('transfer__final_value')),
          order_by=[ExtractYear('date').asc(),ExtractMonth('date').asc()]
        ),
        currency=F('asset__stock_exchange__currency__code')
      ).order_by('year', 'month').distinct('year', 'month').values('date', 'year', 'month', 'accumulated_amount', 'accumulated_spend', 'currency')

      if(len(asset_purchases) == 0):
        asset.prices = []
        continue

      response = urllib.request.urlopen("https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1mo&events=history&includeAdjustedClose=true"%(asset["code"], int(timestamp_beginning), int(time.time())))

      month_prices = [{"date": datetime.date(datetime.strptime(x[0], "%Y-%m-%d")), "value": x[4]} for x in list(csv.reader(response.read().decode().splitlines(), delimiter=','))[1:]]

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
            currency = ""
          else:
            month_price["total_value"] = asset_purchases[index_month-1]["accumulated_amount"] * float(month_price["value"])
            month_price["invested_value"] = asset_purchases[index_month-1]["accumulated_spend"]
            currency = asset_purchases[index_month-1]["currency"]
        else:
          month_price["total_value"] = asset_purchases[index_month]["accumulated_amount"] * month_price["value"]
          month_price["invested_value"] = asset_purchases[index_month]["accumulated_spend"]
          currency = asset_purchases[index_month]["currency"]
          index_month+=1
        
        if(currency == "USD"):
          usd_value = float(usd_prices[index_month]["value"])
          month_price["total_value"] *= usd_value

      asset["prices"] = month_prices  

    months = []
    for i in range(len(assets[0]["prices"])):
      date = assets[0]["prices"][i]["date"]
      # date = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
      month = {"date": date, "total_value": 0, "invested_value": 0}
      for j in range(len(assets)):
        month["total_value"] += assets[j]["prices"][i]["total_value"]
        month["invested_value"] += assets[j]["prices"][i]["invested_value"]
      months.append(month)

    index_saving = 0

    for month in months:
      if(index_saving >= len(savings) or savings[index_saving]["date"] > month["date"]):
        if(index_saving > 0):
          month["total_value"] += savings[index_saving-1]["accumulated_amount"]
          month["invested_value"] += savings[index_saving-1]["accumulated_spend"]
      else:
        month["total_value"] += savings[index_saving]["accumulated_amount"]
        month["invested_value"] += savings[index_saving]["accumulated_spend"]
        index_saving += 1
      date = month["date"]
      month["date"] = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
    
    return render(request, 'Charts/evolution.html', {'assets': months })
