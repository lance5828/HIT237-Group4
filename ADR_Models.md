*** Architectural Decision Record (ADR) for Views ***

# ADR — Anomaly Model

## Title: Design decisions for the Anomaly model

**Context:**
We needed a model to flag unusual observations in the app. I had to decide how it connected to existing models, how severity would be stored, and how to handle deletions.

**Alternatives considered:**
- Link Anomaly directly to Species instead of Observation — rejected because it loses the context of which specific recording was flagged.
- Use plain strings for severity — rejected because nothing stops typos or inconsistent values being saved.
- Write filter logic directly in views — rejected because the same filters would be repeated across multiple places.

**Decision:**
- Linked Anomaly to Observation so the exact recording, location, and observer are always tied to the flag.
- Used Django's TextChoices for severity so valid values are enforced at the model level.
- Used CASCADE for the observation link and PROTECT for the user link to maintain data integrity.
- Created AnomalyQuerySet in managers.py following the same pattern as the existing SpeciesQuerySet and ObservationQuerySet.

**Code reference:** `core/models.py` — Anomaly class, `core/managers.py` — AnomalyQuerySet

**Consequences:**
- Deleting an Observation removes its Anomalies automatically.
- A user account cannot be deleted while they have flagged anomalies on record.
- Query logic is reusable across views and admin without repeating code.