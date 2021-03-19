from django.http import JsonResponse
from ..models import AssetPurchase
import json
import urllib.request
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta, date
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class ServiceViews():
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

  def get_fund_price(request, code):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    url = "https://data.anbima.com.br/fundos/%s"%code

    if "GOOGLE_CHROME_BIN" in os.environ:
      chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
      browser= webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    else:
      browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    # try:
    # except:
    #   chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    #   browser= webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    # finally:
      
    browser.get(url)
    wait = WebDriverWait(browser, 10)
    value = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#output__container--valorDaCota .anbima-ui-output__value > span'))).get_attribute("innerHTML")

    value = float(value[:value.index("<span")].replace("R$&nbsp;", "").replace(",", "."))

    return JsonResponse({"code": code, "price": "%.2f"%value}, safe=False)
    

  # if error: get last available stock price
  def get_stock_price(request, code):
    is_dollar = False
    try:
      response = urllib.request.urlopen("https://query1.finance.yahoo.com/v8/finance/chart/%s"%code) 
      data = json.load(response)

      meta = data.get("chart").get("result")[0].get("meta")
      price = meta.get("regularMarketPrice")
      currency = meta.get("currency")

      if(str(currency) == "USD"):
        is_dollar = True
    except:
      timestamp_beginning = time.mktime((date.today()-timedelta(days=10)).timetuple())

      response = urllib.request.urlopen("https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1d&events=history&includeAdjustedClose=true"%(code, int(timestamp_beginning), int(time.time())))

      prices = [{"date": datetime.date(datetime.strptime(x[0], "%Y-%m-%d")), "value": x[4]} for x in list(csv.reader(response.read().decode().splitlines(), delimiter=','))[1:]]

      if(len(prices) == 0):
        price = 0
      else:
        price = float(prices[-1]["value"])

      if(len(code) < 3 or code[-1] != "A" or code[-2] != "S" or code[-3] != "."):
        is_dollar = True

    if(is_dollar):
      c = CurrencyRates()
      usd_value = c.convert('USD', 'BRL', 1)
      price = price * usd_value

    return JsonResponse({"code": code, "price": "%.2f"%price})

  def get_stock_historical_price(request, code):
    response = urllib.request.urlopen("https://query1.finance.yahoo.com/v7/finance/download/%s?period1=1578928664&period2=%s&interval=1mo&events=history&includeAdjustedClose=true"%(code, int(time.time())))

    prices = [{"date": datetime.strptime(x[0], "%Y-%m-%d"), "value": x[4]} for x in list(csv.reader(response.read().decode().splitlines(), delimiter=','))[1:]]

    return JsonResponse({"code": code, "prices": prices})


  def get_stock_dividends(request, code):

    asset_purchases = AssetPurchase.objects.filter(asset__code=code)

    print(list(asset_purchases))

    response = urllib.request.urlopen("https://query1.finance.yahoo.com/v7/finance/download/%s?period1=1578928664&period2=%s&interval=1d&events=div&includeAdjustedClose=true"%(code, int(time.time())))

    dividends = [{"date": datetime.strptime(x[0], "%Y-%m-%d"), "value": x[1]} for x in list(csv.reader(response.read().decode().splitlines(), delimiter=','))[1:]]

    dividends.sort(key=lambda x: x["date"])

    dividends_sum = 0

    for dividend in dividends:
      sum_stocks = 0
      for purchase in list(asset_purchases):
        if(purchase.date < dividend["date"].date()):
          sum_stocks += purchase.amount
      dividends_sum += sum_stocks * float(dividend["value"])

    return JsonResponse({"code": code, "dividends": dividends, "sum": dividends_sum})
