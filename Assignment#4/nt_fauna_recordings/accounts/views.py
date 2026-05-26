from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    next_page = 'species-list'
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
     template_name = 'accounts/logout.html'


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('species-list')
    
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('species-list')

    return render(request, 'accounts/signup.html', {'form': form})