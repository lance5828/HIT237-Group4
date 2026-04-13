from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .managers import ObservationQuerySet, SpeciesQuerySet, AnomalyQuerySet



class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Species(TimeStampedModel):
    class NTClassification(models.TextChoices):
        CRITICALLY_ENDANGERED = "CR", "Critically Endangered"
        ENDANGERED = "EN", "Endangered"
        VULNERABLE = "VU", "Vulnerable"

    category = models.CharField(max_length=120, db_index=True)
    common_name = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255, unique=True)

    nt_classification = models.CharField(
        max_length=2,
        choices=NTClassification.choices,
        db_index=True,
    )

    epbc_classification = models.CharField(max_length=50, blank=True, null=True)
    introduced_status = models.CharField(max_length=80, blank=True, null=True)
    order_name = models.CharField(max_length=120, blank=True, null=True)
    family = models.CharField(max_length=120, blank=True, null=True)

    objects = SpeciesQuerySet.as_manager()

    class Meta:
        ordering = ["category", "common_name", "scientific_name"]
        verbose_name_plural = "Species"

    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"

    def display_name(self):
        return f"{self.common_name} — {self.scientific_name}"

    def classification_badge(self):
        return self.get_nt_classification_display()



class Observation(TimeStampedModel):
    CONFIDENCE_MIN = 1
    CONFIDENCE_MAX = 10

    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name="observations",
    )

    observer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="observations",
    )

    audio_file = models.FileField(upload_to="observations/audio/%Y/%m/")
    location = models.CharField(max_length=200)

    confidence_score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(CONFIDENCE_MIN),
            MaxValueValidator(CONFIDENCE_MAX),
        ]
    )

    notes = models.TextField(blank=True, default="")

    objects = ObservationQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.species.common_name} at {self.location} (by {self.observer})"

    def has_notes(self):
        return bool(self.notes and self.notes.strip())

    def confidence_label(self):
        if self.confidence_score >= 8:
            return "High"
        elif self.confidence_score >= 5:
            return "Moderate"
        return "Low"
    
    
class Anomaly(TimeStampedModel):

    class Severity(models.TextChoices):
        LOW = "LO", "Low"
        MEDIUM = "ME", "Medium"
        HIGH = "HI", "High"

    observation = models.ForeignKey(
        Observation,
        on_delete=models.CASCADE,
        related_name="anomalies",
    )

    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="flagged_anomalies",
    )

    reason = models.TextField()

    severity = models.CharField(
        max_length=2,
        choices=Severity.choices,
        default=Severity.LOW,
        db_index=True,
    )

    resolved = models.BooleanField(default=False)
    resolved_notes = models.TextField(blank=True, default="")

    objects = AnomalyQuerySet.as_manager()
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Anomalies"

    def __str__(self):
        return f"Anomaly on {self.observation} [{self.get_severity_display()}]"

    def is_critical(self):
        return self.severity == self.Severity.HIGH and not self.resolved