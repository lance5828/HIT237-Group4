*** Architectural Decision Record (ADR) for Views ***

*** Title ***
This project used Class-Based Views (CBVs) with Template Rendering

*** Status ***
Accepted

*** Context ***


*** Decision ***
In this website, we have used Django Class-Based Views (CBVs). In order to execute our application's view layer, we primarily used generic views such as ListView, DetailView, and CreateView.

Breakdown of the implementation of our choices:
DetailView: This is used to display detailed information for a single object.
CreateView: This is used to the form-based creation of the new records in the system
ListView: This is used to display a collection of objects such as the observations, species, and anomalies
template_name: This is used to map each View implemented with its corresponding HTML template
context_object_name: This is used to use simple and meaningful variable names in the templates
reverse_lazy: This is used for a safe URL redirection after submitting forms successfully

By following this approach, we followed Django's Model-View-Template (MVT) architecture. This decreases repetitive code and makes the code easy to interpret.

*** Alternatives Considered ***
#1 Function-Based Views (FBVs) - (Rejected)
Advantages:
They are Simple and easy.
FBVs also provide explicit control over logic and request handling
Disadvantages:
Using FBVs require more repetitive code for simple operations.
It is difficult to maintain consistency across multiple views
Hard to scale for larger applications

*** Consequences ***

Positive consequences:
