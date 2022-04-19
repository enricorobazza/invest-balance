import datetime
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from investments.forms import GuiaBolsoLoginForm
from investments.models import GuiaBolsoToken, GuiaBolsoTransaction, GuiaBolsoCategory, GuiaBolsoCategoryBudget
from investments.api.guiabolso.service import GuiaBolsoService
from django.db.models import Sum, Q, Case, Value, When, BooleanField, F
from itertools import groupby
from operator import attrgetter
from django.db.models.functions import TruncDate

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

		variable, startdate, enddate, ignore, category_ignore, n = GuiaBolsoViews.get_parameters(request)
		transactions = GuiaBolsoTransaction.objects.filter(user=request.user).order_by('-date').select_related('category')
		startdate, enddate = GuiaBolsoViews.decide_date_limits(transactions, n, startdate, enddate)

		amount_inserted = guiabolso_service.update_transactions(startdate, enddate)
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
		monthly = False
		ignore = []
		category_ignore = []
		n = 0

		if 'variable' in request.GET:
			variable = request.GET['variable'] == 'true'
		
		if 'monthly' in request.GET:
			monthly = request.GET['monthly'] == 'true'

		if 'startdate' in request.GET:
			startdate = request.GET['startdate']
			startdate = datetime.datetime.strptime(startdate, "%d/%m/%Y")

		if 'enddate' in request.GET:
			enddate = request.GET['enddate']
			enddate = datetime.datetime.strptime(enddate, "%d/%m/%Y")

		if 'ignore' in request.GET:
			ignore = request.GET['ignore']
			ignore = [int(i) for i in ignore.split(',')]

		if 'category_ignore' in request.GET:
			category_ignore = request.GET['category_ignore']
			category_ignore = [int(i) for i in category_ignore.split(',')]

		if 'n' in request.GET:
			n = int(request.GET['n'])

		return variable, monthly, startdate, enddate, ignore, category_ignore, n

	def find_last_payment(transactions, n, monthly):
		transactions = transactions.filter(Q(label="PAGTO SALARIO")|Q(label="PAGTO ADIANT SALARIAL")).values('date').distinct()

		if len(transactions) == 0:
			return None, None

		if monthly:
			if n is None or n == 0 or len(transactions) == 1:
					if transactions[0]['date'].day < 20: ## end of month
						if len(transactions) > 1:
							return transactions[1]['date'], None
						return transactions[0]['date'], None
					else:								 ## middle of month
						return transactions[0]['date'], None
			
			if 2 * n + 1 > len(transactions): # in case there are no more periods
				last = len(transactions)

				if transactions[last-1]['date'].day > 20: ## end of month
					return transactions[last-1]['date'], transactions[last-3]['date']

				return transactions[last-1]['date'], transactions[last-2]['date']

			add_middle_month = 0
			if transactions[0]['date'].day < 20:
				add_middle_month = 1
			
			return transactions[n*2+add_middle_month]['date'], transactions[(n-1)*2+add_middle_month]['date']
 
		if n is None or n == 0 or len(transactions) == 1: # current period
			return transactions[0]['date'], None

		if n > len(transactions): # in case there are no more periods
			last = len(transactions)
			return transactions[last-1]['date'], transactions[last-2]['date']

		return transactions[n]['date'], transactions[n-1]['date']

	def group_by_category(transactions, last_date):
		result = transactions.values(
			'category__name', 'category__code',
			'category__color', 'category__symbol',
			'category__budget', 'category__budget__month',
			'category__budget__year'
		).annotate(value=Sum('value'))

		result = result.annotate(budget=F('category__budget__goal'), month=F('category__budget__month'), year=F('category__budget__year'))
		result = result.filter(month=last_date.month, year=last_date.year)

		return result.order_by('value')

	def decide_date_limits(transactions, n, startdate, enddate, monthly):
		if startdate is None or n is not None:
			_startdate, _enddate = GuiaBolsoViews.find_last_payment(transactions, n, monthly)
		if enddate is None and _enddate is not None:
			enddate = _enddate - datetime.timedelta(days=1)
		if startdate is None:
			startdate = _startdate

		return startdate, enddate

	def list_transactions(request):
		if request.user.is_anonymous:
			return redirect("login")

		print("Getting transactions")

		variable, monthly, startdate, enddate, ignore, category_ignore, n = GuiaBolsoViews.get_parameters(request)
		transactions = GuiaBolsoTransaction.objects.filter(user=request.user).order_by('-date').select_related('category')
		startdate, enddate = GuiaBolsoViews.decide_date_limits(transactions, n, startdate, enddate, monthly)

		if variable:
			transactions = transactions.filter(Q(category__predictable = False) & Q(exclude_from_variable = False))
			expense_categories = GuiaBolsoCategory.objects.annotate(month_sum = Sum('category_transactions__value')).filter(month_sum__lte = 0).values('id')
			transactions = transactions.filter(category__in=expense_categories)

		transactions = transactions.filter(date__gte=startdate)
		
		if enddate is not None:
			transactions = transactions.filter(date__lte=enddate)

		# Annotate transactions with only ignore by transaction
		# since we dont want to filter out ignored categories
		transactions = transactions.annotate(is_ignored = Case(
			When(code__in=ignore, then=True),
			default=False,
			output_field=BooleanField()
		))
		not_ignored_transactions = transactions.filter(is_ignored=False)

		last_date = enddate
		if len(transactions) > 0 :
			last_date = transactions.order_by('-date')[0].date

		# Generate list of categories based on not ignored transactions
		categories = GuiaBolsoViews.group_by_category(not_ignored_transactions, last_date)
		categories = categories.annotate(is_ignored = Case(
			When(category__code__in=category_ignore, then=True),
			default=False,
			output_field=BooleanField()
		))

		# Annotate the transactions with ignoring the category, not that the categories are created
		transactions = transactions.annotate(is_ignored = Case(
			When(Q(code__in=ignore) | Q(category__code__in=category_ignore), then=True),
			default=False,
			output_field=BooleanField()
		))
		# Update not_ignored list for getting total sum
		not_ignored_transactions = transactions.filter(is_ignored=False)

		total = not_ignored_transactions.aggregate(value=Sum('value'))['value']
		total_planned = categories.filter(is_ignored=False).aggregate(value=Sum('budget'))['value']

		try:
			token = GuiaBolsoToken.objects.get(user=request.user)
		except GuiaBolsoToken.DoesNotExist:
			return redirect('add_token')

		transactions = transactions.annotate(_date=TruncDate('date'))

		# if len(transactions) > 100:
		# 	transactions = transactions[:100]

		return render(request, 'GuiaBolso/list_transactions.html', {
			'transactions': transactions,
			'grouped_transactions': {k: list(v) for k, v in groupby(transactions, attrgetter('_date'))},
			'categories': categories,
			'last_updated': token.last_updated,
			'variable': variable,
			'monthly': monthly,
			'startdate': startdate if startdate is not None else datetime.date.today(),
			'enddate': enddate if enddate is not None else datetime.date.today(),
			'total': total,
			'total_planned': total_planned,
		})
