from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy

from .models import Species, Observation, Anomaly


# -------------------------
# Species Views
# -------------------------

class SpeciesListView(ListView):
    model = Species
    template_name = "core/species_list.html"
    context_object_name = "species_list"


class SpeciesDetailView(DetailView):
    model = Species
    template_name = "core/species_detail.html"
    context_object_name = "species"


# -------------------------
# Observation Views
# -------------------------

class ObservationListView(ListView):
    model = Observation
    template_name = "core/observation_list.html"
    context_object_name = "observations"


class ObservationDetailView(DetailView):
    model = Observation
    template_name = "core/observation_detail.html"
    context_object_name = "observation"


# -------------------------
# Anomaly Views
# -------------------------

class AnomalyListView(ListView):
    model = Anomaly
    template_name = "core/anomaly_list.html"
    context_object_name = "anomalies"


class AnomalyDetailView(DetailView):
    model = Anomaly
    template_name = "core/anomaly_detail.html"
    context_object_name = "anomaly"


class AnomalyCreateView(CreateView):
    model = Anomaly
    template_name = "core/anomaly_form.html"
    fields = ["observation", "flagged_by", "reason", "severity"]
    success_url = reverse_lazy("anomaly-list")