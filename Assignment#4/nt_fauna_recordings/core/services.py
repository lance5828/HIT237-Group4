from django.db import transaction

from .exceptions import (
    ObservationCreateError,
    AnomalyFlagError,
    AnomalyResolveError,
)
from .models import Observation, Anomaly


def create_observation(*, user, species, audio_file, location, confidence_score, notes=""):
    """
    Command service for creating an observation.
    Query/read logic stays in QuerySets; this handles the write workflow.
    """
    if not user or not user.is_authenticated:
        raise ObservationCreateError("You must be logged in to create an observation.")

    if not location or not location.strip():
        raise ObservationCreateError("Location is required.")

    if confidence_score < Observation.CONFIDENCE_MIN or confidence_score > Observation.CONFIDENCE_MAX:
        raise ObservationCreateError("Confidence score must be between 1 and 10.")

    with transaction.atomic():
        return Observation.objects.create(
            species=species,
            observer=user,
            audio_file=audio_file,
            location=location.strip(),
            confidence_score=confidence_score,
            notes=notes or "",
        )


def flag_anomaly(*, user, observation, reason, severity):
    """
    Command service for flagging an observation as anomalous.
    """
    if not user or not user.is_authenticated:
        raise AnomalyFlagError("You must be logged in to flag an anomaly.")

    if not reason or not reason.strip():
        raise AnomalyFlagError("Reason is required.")

    with transaction.atomic():
        return Anomaly.objects.create(
            observation=observation,
            flagged_by=user,
            reason=reason.strip(),
            severity=severity,
        )


def resolve_anomaly(*, user, anomaly, resolved_notes=""):
    """
    Command service for resolving an anomaly.
    """
    if not user or not user.is_authenticated:
        raise AnomalyResolveError("You must be logged in to resolve an anomaly.")

    if anomaly.resolved:
        raise AnomalyResolveError("This anomaly has already been resolved.")

    with transaction.atomic():
        anomaly.resolved = True
        anomaly.resolved_notes = resolved_notes or ""
        anomaly.save(update_fields=["resolved", "resolved_notes", "updated_at"])
        return anomaly