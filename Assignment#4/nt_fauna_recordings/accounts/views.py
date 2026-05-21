from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('species-list')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('species-list')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'accounts/logout.html') # rendering the existing logout html
    return redirect('accounts:login')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('species-list')
    
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('species-list')

    return render(request, 'accounts/signup.html', {'form': form})