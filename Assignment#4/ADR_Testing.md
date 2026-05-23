ADR-003: Testing Strategy

Status: Accepted
Date: 23 May 2026

Context

As the project grew to include a service layer, user authentication, and permission
boundaries, it became important to verify that the core behaviour of the application
worked correctly and that future changes would not break existing functionality.

Without a structured test suite, bugs in the service layer or permission logic could
go unnoticed until runtime, which would be harder to debug and fix.

Decision

A test suite was written using Django's built-in TestCase class. Tests were organised
into four areas:

Model tests verify that model methods return correct values. This includes __str__
output, helper methods like has_notes(), confidence_label(), and is_critical(), and
that model instances behave as expected when their field values change.

Service tests verify that the service functions create_observation(), flag_anomaly(),
and resolve_anomaly() produce the correct outcomes with valid input and raise the
correct custom exceptions when invalid input is provided, such as an unauthenticated
user, a blank location, or an out-of-range confidence score.

View tests verify that all list and detail pages return a 200 status code for
authenticated users, and that the create views redirect correctly after a successful
form submission.

Permission boundary tests verify that unauthenticated users are redirected to the
login page when attempting to access or submit the observation and anomaly create
views. These tests confirm that LoginRequiredMixin is working correctly on those views.

What is not tested includes the admin interface, the data import management command,
file upload storage behaviour, and pagination logic. These were considered lower
priority for this stage of the project because they involve external dependencies or
Django internals that are well tested by the framework itself.

Consequences

The test suite provides confidence that the core write operations and permission
boundaries work correctly. Running the tests with python manage.py test core gives
fast feedback during development.

The tests are tied to the current URL structure and model field names, so if these
change in the future the tests will need to be updated accordingly. This is an
acceptable tradeoff because the tests clearly reflect the intended behaviour of the
application at this stage.