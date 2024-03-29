from django.shortcuts import render
from ..models import Asset, Category, Saving, AssetPurchase
from django.db.models import F, FloatField, Sum
from django.contrib.auth.models import User

class InvestViews():
  @classmethod
  def get_ideal_percentages(cls, user):
    assets = Asset.objects.filter(user=user)

    categories = Category.objects.filter(user=user).aggregate(weight_sum=Sum('weight', output_field=FloatField()))

    saving_categories = Saving.objects.values('category', pk=F('category__pk'), title=F('category__title'), weight=F('category__weight'), can_invest=F('category__can_invest')).filter(user=user).annotate(final_amount=Sum('final_amount', output_field=FloatField()))

    score_sum_by_category = {}

    for asset in assets:
      asset_purchases = AssetPurchase.objects.filter(asset=asset).aggregate(count=Sum(F('amount'), output_field=FloatField()))

      if(asset.can_invest):
        if(asset.category.pk not in score_sum_by_category):
          score_sum_by_category[asset.category.pk] = asset.score
        else:
          score_sum_by_category[asset.category.pk] += asset.score

      if(asset_purchases['count']):
        asset.count = asset_purchases['count']
      else:
        asset.count = 0
    
    for asset in assets:
      category_weight = asset.category.weight / categories["weight_sum"] * 100
      if(asset.can_invest):
        ideal_percentage = asset.score / score_sum_by_category[asset.category.pk] * category_weight
      else:
        ideal_percentage = 0

      asset.category_weight = category_weight
      asset.ideal_percentage = "%.2f" % ideal_percentage  

    initial_patrimony = 0

    for saving_category in saving_categories:
      if saving_category["can_invest"]:
        initial_patrimony += saving_category["final_amount"]
        saving_category["ideal_percentage"] = saving_category["weight"] / categories["weight_sum"] * 100
      else:
        saving_category["ideal_percentage"] = 0
      saving_category["fractioned"] = True
    
    return assets, saving_categories, initial_patrimony


  def make_investment(request):
    if(request.user.is_anonymous):
      user = User.objects.get(pk=1)
    else:
      user = request.user
      # return redirect('/login')

    assets, saving_categories, initial_patrimony = InvestViews.get_ideal_percentages(user)

    return render(request, 'MakeInvestment/makeinvestment.html', {'assets': assets, 'savings': saving_categories, 'initial_patrimony': initial_patrimony})

