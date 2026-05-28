# ADR-001: Introducing a Service Layer Architecture

**Status:** Accepted
**Date:** 27 May 2026

## Context

In the earlier version of the project, most create and update operations were handled directly inside Django views and model forms. Views were responsible for coordinating requests, validating some data, and performing database writes using direct ORM calls such as Observation.objects.create() and Anomaly.objects.create().

While this approach worked for the initial CRUD implementation, it became harder to maintain as the application evolved. New requirements introduced additional business rules, authentication checks, validation rules, transaction handling, and exception management. Keeping this logic inside views risked making them too large and tightly coupled to database behaviour.

The project was already using custom QuerySets to separate reusable read/query logic from the views. However, there was no equivalent structure for write-side workflows such as creating observations, flagging anomalies, or resolving anomalies.

## Decision

To improve the architecture, a dedicated service layer was introduced through services.py. The service layer is responsible for handling command/write workflows, while QuerySets continue handling read/query operations.

The application now follows a lightweight command/query separation approach:

- QuerySets handle filtering, ordering, optimization, and read behaviour.
- Services handle creation, updates, transaction management, and business rule enforcement.

Examples of service-layer commands include:

- create_observation()
- flag_anomaly()
- resolve_anomaly()

The services encapsulate business workflows and use transaction.atomic() to ensure database consistency during multi-step operations. Custom service exceptions were also introduced through exceptions.py to provide clearer separation between business rule failures and Django form validation.

Views were refactored to remain thin controllers that delegate write operations to services and convert service exceptions into user-facing form errors.

## Consequences

This change significantly improved separation of concerns within the project. Views are now smaller and easier to understand because they no longer directly manage business workflows or transactional database behaviour.

The architecture is also more reusable and testable. Since write operations are centralized inside services, the same workflows can later be reused by other interfaces such as APIs, background tasks, or administrative tools without duplicating logic.

The service layer also improved reliability by centralizing transaction management and validation logic. Instead of scattering validation across forms and views, business rules are now enforced consistently in one location.

One drawback is that the application structure became more layered and abstract compared to the original CRUD implementation. Developers must now understand the interaction between views, forms, services, QuerySets, and exceptions. However, this tradeoff was considered worthwhile because it improves maintainability and scalability as the application grows.

## Service Flow Diagram

The diagram below shows how the new service layer works during an observation creation request. The view still receives the form submission, but it does not directly create the database record. Instead, the form handles normal field validation, while the service handles the command-side business rules, transaction management, and exception handling.

This shows the main architectural change made in Assessment 4: the write workflow now moves through a dedicated service layer instead of being handled directly inside the view. If the request is valid, the service creates the record inside a transaction. If a business rule fails, the service raises a custom exception, and the view returns the user to the form with an error instead of allowing an unhandled server error.

![Service Layer Sequence Diagram](Media/service_Layer_Sequence.png)