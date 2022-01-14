from django.shortcuts import render, redirect
from django.http import JsonResponse
from investments.forms import GuiaBolsoLoginForm
from investments.models import GuiaBolsoToken, GuiaBolsoTransaction, GuiaBolsoCategory
from investments.api.guiabolso.service import GuiaBolsoService

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


	def list_transactions(request):
		print("Getting transactions")
		transactions = GuiaBolsoTransaction.objects.filter(user=request.user).order_by('-date').select_related('category')

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
