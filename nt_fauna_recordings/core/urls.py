from django.urls import path
from .views import (
    SpeciesListView, SpeciesDetailView,
    ObservationListView, ObservationDetailView, ObservationCreateView,
    ObservationUpdateView, ObservationDeleteView,
    AnomalyListView, AnomalyDetailView, AnomalyCreateView,
    AnomalyUpdateView, AnomalyDeleteView,
)

urlpatterns = [
    path("species/", SpeciesListView.as_view(), name="species-list"),
    path("species/<int:pk>/", SpeciesDetailView.as_view(), name="species-detail"),

    path("observations/", ObservationListView.as_view(), name="observation-list"),
    path("observations/create/", ObservationCreateView.as_view(), name="observation-create"),
    path("observations/<int:pk>/", ObservationDetailView.as_view(), name="observation-detail"),

    path("anomalies/", AnomalyListView.as_view(), name="anomaly-list"),
    path("anomalies/<int:pk>/", AnomalyDetailView.as_view(), name="anomaly-detail"),
    path("anomalies/create/", AnomalyCreateView.as_view(), name="anomaly-create"),

    # Observation
    path("observations/<int:pk>/edit/", ObservationUpdateView.as_view(), name="observation-edit"),
    path("observations/<int:pk>/delete/", ObservationDeleteView.as_view(), name="observation-delete"),

    # Anomaly
    path("anomalies/<int:pk>/edit/", AnomalyUpdateView.as_view(), name="anomaly-edit"),
    path("anomalies/<int:pk>/delete/", AnomalyDeleteView.as_view(), name="anomaly-delete"),
]
