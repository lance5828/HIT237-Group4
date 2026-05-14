*** Architectural Decision Record (ADR) for Templates ***

# ADR - Template Design

## Title: Design decisions for the template structure and user interface
Models used

*** Status: ***  Accepted

*** Context ***
The system required a well-structured and user-friendly interface to manage multiple pages for species, observations, anomalies, and forms. This involved decisions on template organisation, reuse of common layout elements, and navigation design.

***Alternatives considered:***
- Create separate full HTML structure for each page - *Pro:* simple to implement initially. *Con:* results in repeated code, inconsistent layout, and difficult maintenance. Reject in favour of template inheritance to reduce duplication.

- Include a separate homepage - *Pro:* provides an entry page with navigation links. *Con:* introduces an extra step before accessing core functionality and does not add significant value. Rejected in favour of using the species lista as the system entry point.

Use static navigation without highlighting - *Pro:* simpler implementation. *Con:* users cannot easily identify their current location in the system, reducing usability. Rejected in favour of dynamic navigaion highlighting.

*** Decision ***
- Used Django template inheritance with a shared base template (`base.html`) to ensure consistent layout across all pages.
- Structured templates into list views, detail views, and form views for clarity and maintainability.
- Implemented navigation highlighting using 'request.path' to improve user experience.
- Used Django template tags such as `{%url%}` and variable rendering to dynamically generate links and display data.
- Set the species list page as the system entry point (`/`) instead of creating a separate homepage, allowing users to directly access the main functionality of the system.

*** Code Reference ***
- `core/templates/core/base.html: 8 - 158` - base layout
- `core/templates/core/base.html: 159 - 174` - navigation and highlighting
- `core/templates/core/species_list.html: 8 - 15` -  list rendering
- `nt_fauna_recordings/urls.py` - root URL mapped to species list


*** Consequences ***
- All pages share a consistent layout and navigation structure.
- Reduced code duplication through template inheritance.
- Improved user experience with clear navigation and page highlighting.
- Direct access to core functionality through the species landing page.
- Slightly increased complexity due to use of template inheritance and dynamic rendering.