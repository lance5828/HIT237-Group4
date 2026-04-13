from django.urls import path
from .views import (
    SpeciesListView, SpeciesDetailView,
    ObservationListView, ObservationDetailView,
    AnomalyListView, AnomalyDetailView, AnomalyCreateView,
)

urlpatterns = [
    # Species
    path("species/", SpeciesListView.as_view(), name="species-list"),
    path("species/<int:pk>/", SpeciesDetailView.as_view(), name="species-detail"),

    # Observations
    path("observations/", ObservationListView.as_view(), name="observation-list"),
    path("observations/<int:pk>/", ObservationDetailView.as_view(), name="observation-detail"),

    # Anomalies
    path("anomalies/", AnomalyListView.as_view(), name="anomaly-list"),
    path("anomalies/<int:pk>/", AnomalyDetailView.as_view(), name="anomaly-detail"),
    path("anomalies/create/", AnomalyCreateView.as_view(), name="anomaly-create"),
]

