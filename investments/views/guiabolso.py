from django.shortcuts import render, redirect
from django.http import JsonResponse
from investments.forms import GuiaBolsoLoginForm
from investments.models import GuiaBolsoToken

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

