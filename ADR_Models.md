*** Architectural Decision Record (ADR) for Models ***

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

**Code reference:** `nt_fauna_recordings/core/models.py:103–144` — Anomaly class; `nt_fauna_recordings/core/managers.py:36–56` — AnomalyQuerySet

**Consequences:**
- Deleting an Observation removes its Anomalies automatically.
- A user account cannot be deleted while they have flagged anomalies on record.
- Query logic is reusable across views and admin