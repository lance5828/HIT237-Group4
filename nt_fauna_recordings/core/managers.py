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