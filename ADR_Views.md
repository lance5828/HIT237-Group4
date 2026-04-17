*** Architectural Decision Record (ADR) for Views ***

*** Title ***
This project application used Class-Based Views (CBVs) with Template Rendering

*** Status ***
Accepted

*** Context ***
This application implemented a standard Django framework to develop a server-rendered web application. In this application, the system allows handling of user requests, collecting and managing data from certain models such as Observations, Anomalies and Species and presenting that data through organized and structured templates.

Hence, the Views layer of the application would need to:
- Handle all the incoming HTTP requests from users
- Collect and display collections of individual records (e.g. details) and data (e.g. lists)
- Let users create new records using form submissions
- Support a scalable and reusable web application structure for future developments

Due to all the reasons listed above, we needed to approach the Views structure in a way that reinforces the repetitive nature of viewing, listing, and creating different objects.

*** Decision ***
In this website, we have used Django Class-Based Views (CBVs). In order to execute our application's view layer, we primarily used generic views such as ListView, DetailView, and CreateView.

Breakdown of the implementation of our choices:
- DetailView: This is used to display detailed information for a single object.
- CreateView: This is used to handle the form-based creation of the new records in the system
- ListView: This is used to display a collection of objects such as the observations, species, and anomalies
- template_name: This is used to map each View implemented with its corresponding HTML template
- context_object_name: This is used to use simple and meaningful variable names in the templates
- reverse_lazy: This is used for a safe URL redirection after submitting forms successfully

By following this approach, we followed Django's Model-View-Template (MVT) architecture. This decreases repetitive code and makes the code easy to interpret.

*** Code Reference ***
`nt_fauna_recordings/core/views.py`

*** Alternatives Considered ***
#1 Function-Based Views (FBVs) - (Rejected)
Advantages:
- They are Simple and easy.
- FBVs also provide explicit control over logic and request handling
Disadvantages:
- Using FBVs require more repetitive code for simple operations.
- It is difficult to maintain consistency across multiple views
- Hard to scale for larger applications

*** Consequences ***

Positive consequences:
- CBVs integrate seamlessly with Django templates and make the system easy to use
- It also improves consistency across all the views in our application
- It is good for scalability for larger applications
- It reduces boilerplate code by using the generic views 
- common patterns such as lists, detail, and create are simplified

Negative consequences:
- It is less flexible to use for highly customized logic if we don't extend the base classes
- It requires a good understanding of class inheritance and method overriding
- More things need to be learned or considered compared to function-based views

