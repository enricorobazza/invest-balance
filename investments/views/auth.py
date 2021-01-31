from django.shortcuts import render, redirect
from investments.forms import UserLoginForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

class AuthViews():
  def login(request):
      next = request.GET.get('next')
      if(request.user.is_authenticated):
          return redirect(next or '/')

      form = UserLoginForm(request.POST or None)
      if form.is_valid():
          username = form.cleaned_data.get('username')
          password = form.cleaned_data.get('password')
          user = authenticate(username=username, password=password)
          auth_login(request, user)
          return redirect(next or '/')

      return render(request, 'Accounts/login.html', {'form': form})

  def logout(request):
      auth_logout(request)
      return redirect('/')