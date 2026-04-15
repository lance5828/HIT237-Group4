*** Architectural Decision Record (ADR) for Models ***


# ADR — Species Model

## Title: Design decisions for the Anomaly model

**Status:** Accepted

**Context:**
We needed a model to store the core dataset of threatened species in the Northern Territory. This model acts as the foundation of the application, since all observations must reference a valid species. The main decisions involved how to uniquely identify species, how to enforce classification values, and how to structure the model for efficient querying.

**Alternatives considered:**
- Allow duplicate scientific names — *Pro:* simpler data import, fewer constraints. *Con:* creates ambiguity when linking observations and makes it difficult to uniquely identify species. Rejected because scientific names must act as a unique identifier.
- Store all taxonomy fields as required —  *Pro:* ensures complete data for every species. *Con:* dataset may have missing values, causing import failures and unnecessary complexity. Rejected in favour of optional fields for flexibility.

**Decision:**
- Used scientific_name as a unique field to ensure each species can be reliably identified.
- Implemented NTClassification using Django’s TextChoices to restrict classification values to CR, EN, and VU
- Added a custom SpeciesQuerySet to support domain-specific filtering and querying

**Consequences:**
- Each species is uniquely identifiable, preventing duplication issues.
- Classification values remain consistent and enforceable across the system.
- The model remains flexible for imperfect real-world datasets.
- Query logic can be reused across views and admin through the custom queryset.

**Code Reference:** `nt_fauna_recordings/core/models.py:18–52` — Species class; `nt_fauna_recordings/core/managers.py:4-20` — SpeciesQuerySet 


# ADR — Observation Model
## Title: Design decisions for the Observation model

**Status:** Accepted

**Context:**
We needed a model to capture user-submitted observations of species, including audio recordings and contextual information such as location and confidence level. The main challenge was ensuring strong relationships with existing data while allowing flexibility for user input.

**Alternatives considered:**
- Allow observations without linking to a species — *Pro:* easier user input, less strict validation. *Con:* breaks the purpose of the system since observations would not be tied to known species. Rejected to maintain data integrity.
- Store confidence score as free text — *Pro:* flexible descriptions like "high" or "low". *Con:* inconsistent values and difficult to filter or analyse. Rejected in favour of numeric scoring with validation.
- Embed anomaly flags directly in Observation — *Pro:* simpler structure with fewer models. *Con:* limits ability to track multiple anomaly reports and mixes validation logic with core data. Rejected in favour of a separate Anomaly model

**Decision:**
- Linked Observation to Species using a foreign key with PROTECT to prevent accidental deletion of referenced species.
- Linked Observation to the User model to track who recorded the observation.
- Implemented confidence_score as an integer with validation between 1 and 10.
- Used a FileField to support audio uploads as part of each observation.
- Created ObservationQuerySet to encapsulate reusable query logic

**Consequences:**
- Observations are always tied to valid species, ensuring data consistency.
- Users can upload audio evidence, supporting the project’s core functionality.
- Confidence scores are structured and easy to filter or analyse.
- Query logic is reusable and consistent across the system.

**Code reference:** `nt_fauna_recordings/core/models.py:56-100` — Observation class; `nt_fauna_recordings/core/managers.py:23-34` — ObservationQuerySet


# ADR — TimeStampedModel
## Title: Design decisions for the shared TimeStampedModel

**Status:** Accepted

**Context:**
Multiple models in the system required tracking of creation and update timestamps. Without a shared solution, each model would need to define these fields separately, leading to duplication and potential inconsistency

**Alternatives considered:**
- Define timestamp fields in each model individually — Pro: straightforward and explicit. Con: repetitive code and higher risk of inconsistency. Rejected due to duplication.

**Decision:**
- Created an abstract base class TimeStampedModel containing created_at and updated_at fields.
- Made other models inherit from this class to ensure consistent timestamp tracking

**Consequences:**
- Eliminates duplication across models.
- Ensures consistent timestamp behaviour throughout the application.
- Makes it easier to extend or modify timestamp logic in one place.

**Code reference:** `nt_fauna_recordings/core/models.py:5–13` — TimeStampedModel


# ADR — Anomaly Model

## Title: Design decisions for the Anomaly model

**Status:** Accepted

**Context:**
We needed a model to flag unusual observations in the app. I had to decide how it connected to existing models, how severity would be stored, and how to handle deletions.

**Alternatives considered:**
- Link Anomaly directly to Species instead of Observation — *Pro:* simpler relationship, fewer joins. *Con:* loses the context of which specific recording was flagged, making it impossible to trace the anomaly back to the audio file, location, or observer. Rejected for this reason.
- Use plain strings for severity — *Pro:* flexible, no extra class required. *Con:* nothing stops typos or inconsistent values being saved, and the database has no constraint to enforce valid options. Rejected in favour of `TextChoices` which enforces valid values at the model level.
- Write filter logic directly in views — *Pro:* quick to implement for a single use case. *Con:* the same filters would need to be repeated across every view that queries anomalies, violating DRY. Rejected in favour of a dedicated `AnomalyQuerySet`.

**Decision:**
- Linked Anomaly to Observation so the exact recording, location, and observer are always tied to the flag.
- Used Django's TextChoices for severity so valid values are enforced at the model level.
- Used CASCADE for the observation link and PROTECT for the user link to maintain data integrity.
- Created AnomalyQuerySet in managers.py following the same pattern as the existing SpeciesQuerySet and ObservationQuerySet.

**Consequences:**
- Deleting an Observation removes its Anomalies automatically.
- A user account cannot be deleted while they have flagged anomalies on record.
- Query logic is reusable across views and admin

**Code reference:** `nt_fauna_recordings/core/models.py:103–144` — Anomaly class; `nt_fauna_recordings/core/managers.py:36–56` — AnomalyQuerySet