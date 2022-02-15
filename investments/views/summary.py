from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..models import AssetPurchase, Saving
from django.db.models import F, Sum, FloatField, Case, When, Q
from django.contrib.auth.models import User
from investments.forms import CategoryForm

class SummaryViews():
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
      assets = AssetPurchase.objects.values(code=F('asset__code'), invest_type=F('asset__invest_type')).filter(asset__category=category["pk"]).annotate(amount=Sum('amount'))
      ret_category = {}
      ret_category["pk"] = category["pk"]
      ret_category["title"] = category["title"]
      ret_category["sum"] = "%.2f" % category["sum"]
      ret_category["assets"] = list(assets.values("code", "amount", "invest_type"))
      ret_categories[category["pk"]] = ret_category

    saving_categories = Saving.objects.values(title=F('category__title')).filter(user=user).annotate(
      current_value=Sum('final_amount', output_field=FloatField()), 
      sum=Sum('amount', output_field=FloatField()), 
      yield_rate = Case(
        When(sum=0, then=0),
        default=(F('current_value') - F('sum'))/F('sum')
      )
    )

    initial_patrimony = 0

    for saving in saving_categories:
      total_sum += saving["sum"]
      initial_patrimony += saving["current_value"]
      saving["yield"] = "%.2f" % (saving["yield_rate"] * 100)

    return render(request, 'Summary/summary.html', {'categories': list(ret_categories.values()), 'total_sum': "%.2f"%total_sum, 'savings': saving_categories, 'saving_categories':  list(saving_categories),'initial_patrimony': initial_patrimony})
  
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