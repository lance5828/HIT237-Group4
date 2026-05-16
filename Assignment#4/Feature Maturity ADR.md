ADR-001: Moving Query Logic into Custom QuerySets

Status: Accepted
Date: 14 May 2026

Context

At the start of the project, the views directly handled most database queries using simple ORM calls like Species.objects.all() and Observation.objects.all(). This worked fine early on, but as the project grew, more filtering, ordering, and optimization logic started getting added into the views.

Over time, this made the views larger and harder to maintain. It also went against Django’s “fat models, skinny views” philosophy, where reusable database logic should stay inside the model layer instead of the views.

Decision

To improve the structure of the project, custom QuerySet classes were introduced for the Species, Observation, and Anomaly models. Reusable query methods such as threatened(), recent(), critical(), and search_by_name() were added to handle filtering and ordering logic.

Later, higher-level methods like homepage(), list_page(), and detail_page() were added to make the views even smaller and cleaner.

The project uses Django’s as_manager() approach so these QuerySet methods can be accessed directly through objects.

Consequences

This change made the views much cleaner because they now mainly handle templates and page configuration instead of database logic. Query behaviour is reusable and easier to maintain since it is centralized inside QuerySets.

The structure is also easier to expand later if more filters, search features, or optimizations are needed. Using methods like select_related() also helped improve database efficiency when loading related objects.

One downside is that the project now has a bit more abstraction, which can be slightly harder to understand at first for beginners.



ADR-004: Optimizing Related Object Queries

Status: Accepted
Date: 14 May 2026

Context

In the earlier version of the project, related objects such as species, observers, and flagged users were loaded separately whenever observations or anomalies were displayed. This caused additional database queries to be executed when rendering pages with related foreign key data.

As more records were added to the system, this approach became less efficient and could potentially affect performance.

Decision

To improve query efficiency, the project introduced Django’s select_related() inside custom QuerySet methods such as recent() and detail_page().

This allows related foreign key data to be loaded in a single optimized database query instead of multiple separate queries.

Consequences

This improvement reduced unnecessary database hits and improved page performance when displaying observations and anomalies with related species and user information.

The optimization also kept the views clean because the query optimization logic remains inside the QuerySet layer rather than being repeated across multiple views.