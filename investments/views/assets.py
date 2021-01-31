from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..models import Asset, AssetPurchase
from django.db.models import Sum, F, FloatField
from django.contrib.auth.models import User
from investments.forms import AssetForm

class AssetsViews():
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