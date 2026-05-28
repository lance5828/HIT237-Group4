## ADR-002: Usage of Login_view and Logout_view for authentication

Status: Accepted
Date: 19 May 2026

## Context

Previously the website had no form of authentication for the users. At that time anyone with access to the website could edit, update or delete the observations. This increases security risks and is hard to track who made changes to the observations and anomalies.

Authentication is required to authenticate users to protect specific views such as creating and updating observations and anomalies.

Django has built-in class-based views ('LoginView', 'LogoutView') and low-level 'login()' and 'logout()' functions from 'django.contrib.auth'.

## Decision

We used Django's built-in class-based views for 'UserLoginView' and 'UserLogoutView' by subclassing 'LoginView' and 'LogoutView' from the 'django.contrib.auth.views'. Since there is no built-in class based view in Django for Signup View, we used a custom function-based view for 'signup-view' using Django's 'login()' function and 'UserCreationForm'.

Implementation:

- UserLoginView - Using Django's built-in class view 'LoginView'. It redirects the users who are already authenticated through 'redirect_authenticated_user = True'. If the user logins successfully, it redirects them to 'species-list' through 'next_page'. It also supports '?next=' through an input in the template so that the users can access the page they initially wanted to visit after loggin in.

- UserLogoutView - Django's built-in class view 'LogoutView' was used. It renders 'accounts/logout.html' directly after logging out through 'template-name'.

- signup_view - In order to handle new user registrations, a custom function-based view called 'UserCreationForm' was used. When the user are already authenticated, they are redirected to 'species-list'. If the users can signup successfully, they are logged in and redirected to 'species-list'.

In a nutshell, the authentication for users was setup using CBVs since using Django's built-in functionality from login and logout views reduce boilerplate code. FBVs were used for the signup view since there is no pre-built Django class based view for it.

## Consequences

** Positive **
- 'UserLoginView' and 'UserLogoutView' reduces boilerplate code and adheres to fat models, skinny views Django principle by using built-in Django CBVs
- 'signup_view' is easy to read and interpret as FBV is used
- 'redirect_authenticated_user = True' smoothly handles users who are already authenticated without need for manual redirection logic.
- No manual checking needed for POST-only logout since Djnago's 'LogoutView' handles it itself.

** Negative **
- Since we are mixing CBVs and FBVs in the exact same file, it can be inconsistent for some. However, it is a practical Django pattern.
- Customizing 'UserLoginView' or 'UserLogoutView' beyond 'next_page' and 'template_name' would require overriding the CBV method which in turn would add to complexity.
- At this stage 'UserCreationForm' only allows fundamental options like username and password which may require replacing later on with a custom form when the website is developed.

## ADR-005: Usage of LoginRequiredMixin in core/views.py for authentication

Status: Accepted
Date: 26 May 2026

## Context

In the website we have used several views to manage Observations, Anomalies, and Species. Many of these views are in read-only method and are accessible to all. However, some of the other views have write operations (create, update, delete) available that should be accessed only by authenticated users. We had to implement a way of authentication and secure the write views without repeating the authentication logic manually across each of them and increasing the boilerplate.

## Decision

Therefore, we used 'LoginRequiredMixin' from 'django.contrib.auth.mixins' fro create, delete, and update views for both Anomalies and Observations. Other read-only views such as detail and list were left accessible.

Views that have 'LoginRequiredMixin' enabled:
- 'ObservationCreateView' - Authenticated users have the access to submit a new observation
- 'ObservationUpdateView' - Authenticated users have the access to edit an observation that exists in the application
- 'ObservationDeleteView' - Authenticated users can delete existing observations
- 'AnomalyCreateView' - The authenticated users can flag an anomaly
- 'AnomalyUpdateView' - The authenticated users are allowed to edit an anomaly that already exists
- 'AnomalyDeleteView' - The authenticated users can delete an existing anomaly

Following the correct Djnago convention, 'LoginRequiredMixin' was placed as the first class in the inheritance chain for the secured views. Hence, the authentication check is implemented before running other view logics in the application.

Consequences

The write operations are protected from unauthenticated users since only authenticated users can edit them. The read-only views are accesible to all. There is also a clear and consistent Django pattern across all the protected views without having any duplicated logic.

On the other hand, 'LoginRequiredMixin' depends on 'settings.LOGIN_URL' being correctly configured. To avoid any crash of the application, the setting has to be updated simultaneously in case the login URL changes.