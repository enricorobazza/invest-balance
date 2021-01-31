from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import F
from ..models import AssetPurchase
from investments.forms import AssetPurchaseForm, TransferForm, SavingForm
from datetime import datetime

class HistoryViews():
  def history(request):
    if(request.user.is_anonymous):
      user = User.objects.get(pk=1)
    else:
      user = request.user
      # return redirect('/login')

    purchases = AssetPurchase.objects.values("asset", "date", "amount", paid_value=(F('value')+F('taxes_value')/F('amount'))*F('transfer__value')/F('transfer__final_value'), total_value=(F('value')*F('amount')+F('taxes_value'))*F('transfer__value')/F('transfer__final_value'), code=F("asset__code"), short_code=F("asset__short_code")).filter(asset__user = user).order_by('-date')

    return render(request, 'History/history.html', {'purchases': purchases})

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