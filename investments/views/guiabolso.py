import datetime
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from investments.forms import GuiaBolsoLoginForm
from investments.models import GuiaBolsoToken, GuiaBolsoTransaction, GuiaBolsoCategory
from investments.api.guiabolso.service import GuiaBolsoService
from django.db.models import Sum, Q

class GuiaBolsoViews():
	def add_token(request):
		if request.method == 'POST':
			data = request.POST.copy()
			data['user'] = request.user

			form = GuiaBolsoLoginForm(data)

			if form.is_valid():
				asset = form.save(request.user)
				return redirect('/')
			else:
				print(form.errors)
				return JsonResponse({'success': False, 'errors': form.errors}, safe=False)
		else:
			form = GuiaBolsoLoginForm()
			return render(request, 'GuiaBolso/add_token.html', {
				'form': form
			})

	def refresh_transactions(request):
		guiabolso_service = GuiaBolsoService(request.user)
		amount_inserted = guiabolso_service.update_transactions()
		if amount_inserted < 0:
			return redirect('add_token')

		params = ""
		for key in request.GET:
			params += f"{key}={request.GET[key]}&"		

		return redirect(f"{reverse('list_guiabolso')}?{params[:-1]}")

	def get_parameters(request):
		variable = False
		startdate = None
		enddate = None
		n = 0

		if 'variable' in request.GET:
			variable = request.GET['variable'] == 'true'

		if 'startdate' in request.GET:
			startdate = request.GET['startdate']
			startdate = datetime.datetime.strptime(startdate, "%d/%m/%Y")

		if 'enddate' in request.GET:
			enddate = request.GET['enddate']
			enddate = datetime.datetime.strptime(enddate, "%d/%m/%Y")

		if 'n' in request.GET:
			n = int(request.GET['n'])

		return variable, startdate, enddate, n

	def find_last_payment(transactions, n):
		transactions = transactions.filter(Q(label="PAGTO SALARIO")|Q(label="PAGTO ADIANT SALARIAL")).values('date').distinct()

		if len(transactions) == 0:
			return None, None

		if n is None or n == 0 or len(transactions) == 1:
			return transactions[0]['date'], None

		if n > len(transactions):
			last = len(transactions)
			return transactions[last-1]['date'], transactions[last-2]['date']

		return transactions[n]['date'], transactions[n-1]['date']

	def group_by_category(transactions):
		result = transactions.values(
			'category__name', 'category__code',
			'category__color', 'category__symbol'
		).annotate(value=Sum('value'))
		return result.order_by('value')

	def list_transactions(request):
		variable, startdate, enddate, n = GuiaBolsoViews.get_parameters(request)

		print("Getting transactions")
		transactions = GuiaBolsoTransaction.objects.filter(user=request.user).order_by('-date').select_related('category')

		if startdate is None or n is not None:
			startdate, _enddate = GuiaBolsoViews.find_last_payment(transactions, n)
			if enddate is None:
				enddate = _enddate

		if variable:
			transactions = transactions.filter(Q(category__predictable = False) & Q(exclude_from_variable = False))
			expense_categories = GuiaBolsoCategory.objects.annotate(month_sum = Sum('category_transactions__value')).filter(month_sum__lte = 0).values('id')
			transactions = transactions.filter(category__in=expense_categories)

		transactions = transactions.filter(date__gte=startdate)

		if enddate is not None:
			transactions = transactions.filter(date__lte=enddate)

		categories = GuiaBolsoViews.group_by_category(transactions)
		total = transactions.aggregate(value=Sum('value'))['value']

		if len(transactions) > 100:
			transactions = transactions[:100]

		try:
			token = GuiaBolsoToken.objects.get(user=request.user)
		except GuiaBolsoToken.DoesNotExist:
			return redirect('add_token')

		return render(request, 'GuiaBolso/list_transactions.html', {
			'transactions': transactions,
			'categories': categories,
			'last_updated': token.last_updated,
			'variable': variable,
			'startdate': startdate,
			'enddate': enddate,
			'total': total
		})
