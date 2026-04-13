from turtle import home

from django.urls import path
from .views import (
    home,
    SpeciesListView, SpeciesDetailView,
    ObservationListView, ObservationDetailView, ObservationCreateView,
    AnomalyListView, AnomalyDetailView, AnomalyCreateView,
)

urlpatterns = [
    # Home
    path("", home, name="home"),
   
    # Species
    path("species/", SpeciesListView.as_view(), name="species-list"),
    path("species/<int:pk>/", SpeciesDetailView.as_view(), name="species-detail"),

    # Observations
    path("observations/", ObservationListView.as_view(), name="observation-list"),
    path("observations/<int:pk>/", ObservationDetailView.as_view(), name="observation-detail"),
    path("observations/create/", ObservationCreateView.as_view(), name="observation-create"),

    # Anomalies
    path("anomalies/", AnomalyListView.as_view(), name="anomaly-list"),
    path("anomalies/<int:pk>/", AnomalyDetailView.as_view(), name="anomaly-detail"),
    path("anomalies/create/", AnomalyCreateView.as_view(), name="anomaly-create"),
]

