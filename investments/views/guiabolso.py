from django.shortcuts import render, redirect
from django.http import JsonResponse
from investments.forms import GuiaBolsoLoginForm
from investments.models import GuiaBolsoToken, GuiaBolsoTransaction, GuiaBolsoCategory
from investments.api.guiabolso.service import GuiaBolsoService
from django.db.models import Sum

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

		return redirect('list_guiabolso')

	def get_parameters(request):
		variable = False
		if 'variable' in request.GET:
			variable = request.GET['variable'] == 'true'

		expenses = False
		if 'expenses' in request.GET:
			expenses = request.GET['expenses'] == 'true'

		return variable, expenses

	def list_transactions(request):
		variable, expenses = GuiaBolsoViews.get_parameters(request)

		print("Getting transactions")
		transactions = GuiaBolsoTransaction.objects.filter(user=request.user).order_by('-date').select_related('category')

		if variable:
			transactions = transactions.filter(category__predictable = False)

		if expenses:
			expense_categories = GuiaBolsoCategory.objects.annotate(month_sum = Sum('category_transactions__value')).filter(month_sum__lte = 0).values('id')
			transactions = transactions.filter(category__in=expense_categories)

		if len(transactions) > 100:
			transactions = transactions[:100]

		try:
			token = GuiaBolsoToken.objects.get(user=request.user)
		except GuiaBolsoToken.DoesNotExist:
			return redirect('add_token')

		return render(request, 'GuiaBolso/list_transactions.html', {
			'transactions': transactions,
			'last_updated': token.last_updated,
		})
