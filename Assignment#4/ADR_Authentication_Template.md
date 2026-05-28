# ADR - 006: Authentication Interface Design

Status: Accepted
Date: 26 May 2026

## Context

In the assessment 2, we do not apply any authentication interface (login, logout, signup). Every user can access to the existing NT fauna Recordings system without authenticate. There was no login, logout and signup pages and always fully visible for the navigation bar whether the use get authenticated or not.

The need of authentication user interface:
- The existing NT Fauna Recordings design have to be same such as theme, colour, font type and layout.
- There are two separate of users, one is authenticated users which can create, update and delete the observation and report anomaly, another is unauthenticated users which only can view the detail.
- The way to track who made changes when we apply authentication pages.
 
## Decision

A separate accounts app was created with its own templates folder to isolate all authentication-related interface code from the core application.

Three templates were created:

- login.html — handles two states in a single template:
  * If user is authenticated: shows the NT Fauna Recordings landing page which is species list, can create, update and delete.
  * If user is not authenticated: only can view the species list, there login and register button on top to get authenticated if needed.

- signup.html — registration form with username, password, and confirm password fields. On successful registration, the user will auto-logged in, do not need to login again.

- logout.html — confirmation page shown after the user has been signed out, with a link back to the login page.

All three templates extend base.html using Django's template inheritance system ({% extends 'base.html' %}), which means they automatically inherit the header, navigation bar, footer, and all CSS classes (.btn, .badge, .card) without duplicating any styling.

The navigation bar in base.html was updated to conditionally render based on authentication state using {% if user.is_authenticated %}:
- Unauthenticated users see only Login and Register links on the top right
- Authenticated users see the full navigation links on the left and a "Hi, username" greeting with a Logout button on the far right

## Consequences

Positive:
- Template inheritance ensures all auth pages are visually consistent with the rest of the application with zero duplicated CSS or layout code
- Conditional navigation bar prevents unauthenticated users from seeing links they cannot access, improving UX clarity
- Separating accounts into its own app keeps authentication concerns isolated from core business logic
- POST-only logout with CSRF token protects against forced logout attacks
- Generic error messages on the login form protect against username enumeration attacks
- Redirecting to login after signup ensures the authentication flow is explicit and independently testable

Negative:
- Inline styles are used in templates rather than dedicated CSS classes in a stylesheet, which reduces reusability if the design system changes in the future
- The password visibility toggle relies on vanilla JavaScript which is not covered by the test suite
- UserCreationForm only collects username and password — no email field is included, which limits future account recovery options
- Staff status must be assigned manually through the Django admin panel, there is no self-service role assignment for users 