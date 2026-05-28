ADR-002: Usage of Login_view and Logout_view

Status: Accepted
Date: 19 May 2026

Context

Previously the website had no form of authentication for the users. At that time anyone with access to the website could edit, update or delete the observations. This increases security risks and is hard to track who made changes to the observations and anomalies.

Authentication is required to authenticate users to protect specific views such as creating and updating observations and anomalies.

Django has built-in class-based views ('LoginView', 'LogoutView') and low-level 'login()' and 'logout()' functions from 'django.contrib.auth'.

Decision

We used Django's built-in class-based views for 'UserLoginView' and 'UserLogoutView' by subclassing 'LoginView' and 'LogoutView' from the 'django.contrib.auth.views'. Since there is no built-in class based view in Django for Signup View, we used a custom function-based view for 'signup-view' using Django's 'login()' function and 'UserCreationForm'.

Implementation:

- UserLoginView - Using Django's built-in class view 'LoginView'. It redirects the users who are already authenticated through 'redirect_authenticated_user = True'. If the user logins successfully, it redirects them to 'species-list' through 'next_page'. It also supports '?next=' through an input in the template so that the users can access the page they initially wanted to visit after loggin in.

- UserLogoutView - Django's built-in class view 'LogoutView' was used. It renders 'accounts/logout.html' directly after logging out through 'template-name'.

- signup_view - In order to handle new user registrations, a custom function-based view called 'UserCreationForm' was used. When the user are already authenticated, they are redirected to 'species-list'. If the users can signup successfully, they are logged in and redirected to 'species-list'.

In a nutshell, the authentication for users was setup using CBVs since using Django's built-in functionality from login and logout views reduce boilerplate code. FBVs were used for the signup view since there is no pre-built Django class based view for it.

Consequences

** Positive **
- 'UserLoginView' and 'UserLogoutView' reduces boilerplate code and adheres to fat models, skinny views Django principle by using buil-in Django CBVs
- 'signup_view' is easy to read and interpret as FBV is used
- 'redirect_authenticated_user = True' smoothly handles users who are already authenticated without need for manual redirection logic.
- No manual checking needed for POST-only logout since Djnago's 'LogoutView' handles it itself.

** Negative **
- Since we are mixing CBVs and FBVs in the exact same file, it can be inconsistent for some. However, it is a practical Django pattern.
- Customizing 'UserLoginView' or 'UserLogoutView' beyond 'next_page' and 'template_name' 

ADR-005: Usage of LoginRequiredMixin in core/views.py

Status: Accepted
Date: 26 May 2026

Context

Decision

Consequences