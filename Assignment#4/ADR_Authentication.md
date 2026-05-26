ADR-002: Usage of Login_view and Logout_view

Status: Accepted
Date: 19 May 2026

Context

Previously the website had no form of authentication for the user. At that time anyone with access to the website could edit, update or delete the observations. This increases security risks and is hard to track who made changes to the observations and anomalies.

Authentication is required to authenticate users to protect specific views such as creating and updating observations and anomalies.

Django has built-in class-based views ('LoginView', 'LogoutView') and low-level 'login()' and 'logout()' functions from 'django.contrib.auth'.

Decision

We used Django's built-in class-based views for 'UserLoginView' and 'UserLogoutView' by subclassing 'LoginView' and 'LogoutView' from the 'django.contrib.auth.views'. Since there is no built-in class based view in Django for Signup View, we used a custom function-based view for 'signup-view' using Django's 'login()' function and 'UserCreationForm'.

Implementation:

- UserLoginView - Using Django's built-in class view 'LoginView'. It redirects the users who are already authenticated through 'redirect_authenticated_user = True'. If the user logins successfully, it redirects them to 'species-list' through 'next_page'. It also supports '?next=' through an input in the template so that the users can access the page they initially wanted to visit after loggin in.

- UserLogoutView - Django's 

Consequences

ADR-005: Usage of LoginRequiredMixin in core/views.py

Status: Accepted
Date: 26 May 2026

Context

Decision

Consequences