from django.db import models


class SpeciesQuerySet(models.QuerySet):
    THREATENED_CLASSIFICATIONS = ("CR", "EN", "VU")

    def threatened(self):
        return self.filter(nt_classification__in=self.THREATENED_CLASSIFICATIONS)

    def by_category(self, category: str):
        return self.filter(category__iexact=category)

    def ordered_for_homepage(self):
        return self.order_by("category", "common_name", "scientific_name")

    def search_by_name(self, term: str):
        return self.filter(
            models.Q(common_name__icontains=term)
            | models.Q(scientific_name__icontains=term)
        )


class ObservationQuerySet(models.QuerySet):
    def recent(self):
        return self.select_related("species", "observer").order_by("-created_at")

    def for_species(self, species):
        return self.filter(species=species)

    def high_confidence(self, threshold: int = 7):
        return self.filter(confidence_score__gte=threshold)

    def with_notes(self):
        return self.exclude(notes__exact="").exclude(notes__isnull=True)
    
class AnomalyQuerySet(models.QuerySet):

    def unresolved(self):
        return self.filter(resolved=False)

    def resolved(self):
        return self.filter(resolved=True)

    def critical(self):
        return self.filter(severity="HI", resolved=False)

    def for_observation(self, observation):
        return self.filter(observation=observation)

    def by_severity(self, severity: str):
        return self.filter(severity__iexact=severity)

    def recent(self):
        return self.select_related(
            "observation", "flagged_by"
        ).order_by("-created_at")