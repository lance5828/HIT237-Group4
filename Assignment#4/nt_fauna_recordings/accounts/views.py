from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect

class UserLoginView(LoginView):
    """
    This is used for handling User authentication / login by implementing Django's built-in LoginView.
    The unauthenticated users will see the form through accounts/login.html
    Authenticated users are immediately redirected to species-list through redirect_authenticated_user removing the need for extra logins.
    """
    template_name = 'accounts/login.html'
    next_page = 'species-list'
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
     """
     Used for handling user logouts implementing by using Django's built-in LogoutView.
     By default, Django's LogoutView enforces the POST-only logout to prevent logout from accidental GET requests.
     After logging out successfully, accounts/logout.html is directly rendered.
     """
     template_name = 'accounts/logout.html'


def signup_view(request):
    """
    Used for handling new user registrations by using Django's built-in UserCreationForm.
    If the user is already authenticated, they are redirected to species-list which prevents redundant registration attempts.
    For a valid POST, the new registered user gets saved in the system, gets immediately logged in and redirected to the species-list. for an invalid POST or get request, the signup form is rendered through accounts/signup.html.
    """
    if request.user.is_authenticated:
        return redirect('species-list')
    
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('species-list')

    return render(request, 'accounts/signup.html', {'form': form})