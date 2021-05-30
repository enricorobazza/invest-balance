from django.shortcuts import render, redirect
from django.http import JsonResponse
from investments.services.efficient_frontier import trace_by_time
from django.contrib.auth.models import User
from investments.models import Asset
from investments.views.invest import InvestViews

class RiskViews():
  def efficient_frontier(request, category = -1):
    if(request.user.is_anonymous):
        user = User.objects.get(pk=1)
    else:
        user = request.user

    assets, saving_categories, initial_patrimony = InvestViews.get_ideal_percentages(user)
    filtered_assets = []
    
    for asset in assets:
        if(category > 0 and asset.category.pk != category):
            continue
        if asset.invest_type == "S" and asset.can_invest:
            filtered_assets.append(asset)

    assets = filtered_assets

    if(len(assets) == 0):
        return render(request, "Risk/efficient_frontier.html", {})

    stocks = [asset.code for asset in assets]
    weights = [float(asset.ideal_percentage) for asset in assets]
    # stocks = ['EZTC3.SA', 'WEGE3.SA', 'TEND3.SA', 'EGIE3.SA', 'ITSA3.SA', 'FLRY3.SA', 'MGLU3.SA', 'B3SA3.SA', 'ENBR3.SA', 'ABEV3.SA', 'COKE', 'GOOGL', 'AMZN']
    # weights = [1.48, 1.63, 1.71, 2.13, 2.09, 2.03, 1.91, 1.86, 1.76, 2, 0.96, 5.77, 5.77]
    
    return render(request, "Risk/efficient_frontier.html", {"graph": trace_by_time(stocks, weights)})