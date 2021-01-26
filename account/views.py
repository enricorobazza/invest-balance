from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from account.models import User
from account.forms import UserLoginForm, UserCreationForm
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils import timezone
from django.http import JsonResponse

# Create your views here.

def login(request):
    next = request.GET.get('next')
    if(request.user.is_authenticated):
        return redirect(next or '/')

    form = UserLoginForm(request.POST or None)

    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        auth_login(request, user)
        return redirect(next or '/')

    return render(request, 'login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('/')

def signup(request):
    if request.method == 'POST':
        data = request.POST.copy()
        form = UserCreationForm(data)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            auth_login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
