from django.contrib import admin

from .models import Observation, Species


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        "common_name",
        "scientific_name",
        "category",
        "nt_classification",
        "epbc_classification",
        "introduced_status",
    )
    list_filter = ("category", "nt_classification", "introduced_status")
    search_fields = ("common_name", "scientific_name")
    ordering = ("category", "common_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = (
        "species",
        "observer",
        "location",
        "confidence_score",
        "created_at",
    )
    list_filter = ("confidence_score", "created_at", "species__nt_classification")
    search_fields = ("species__common_name", "species__scientific_name", "location")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("species", "observer")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("species", "observer")
