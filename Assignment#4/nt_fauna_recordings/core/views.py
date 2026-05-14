from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Species, Observation, Anomaly


# -------------------------
# Species Views
# -------------------------

class SpeciesListView(ListView):
    model = Species
    template_name = "core/species_list.html"
    context_object_name = "species_list"
    paginate_by = 7
    queryset = Species.objects.homepage()


class SpeciesDetailView(DetailView):
    model = Species
    template_name = "core/species_detail.html"
    context_object_name = "species"
    queryset = Species.objects.detail_page()


# -------------------------
# Observation Views
# -------------------------

class ObservationListView(ListView):
    model = Observation
    template_name = "core/observation_list.html"
    context_object_name = "observations"
    paginate_by = 10
    queryset = Observation.objects.list_page()


class ObservationDetailView(DetailView):
    model = Observation
    template_name = "core/observation_detail.html"
    context_object_name = "observation"
    queryset = Observation.objects.detail_page()


class ObservationCreateView(CreateView):
    model = Observation
    template_name = "core/observation_form.html"
    fields = ["species", "observer", "audio_file", "location", "confidence_score", "notes"]
    success_url = reverse_lazy("observation-list")


class ObservationUpdateView(UpdateView):
    model = Observation
    template_name = "core/observation_form.html"
    fields = ["species", "observer", "audio_file", "location", "confidence_score", "notes"]
    success_url = reverse_lazy("observation-list")
    queryset = Observation.objects.form_page()


class ObservationDeleteView(DeleteView):
    model = Observation
    template_name = "core/observation_confirm_delete.html"
    success_url = reverse_lazy("observation-list")
    queryset = Observation.objects.form_page()


# -------------------------
# Anomaly Views
# -------------------------

class AnomalyListView(ListView):
    model = Anomaly
    template_name = "core/anomaly_list.html"
    context_object_name = "anomalies"
    paginate_by = 10
    queryset = Anomaly.objects.list_page()


class AnomalyDetailView(DetailView):
    model = Anomaly
    template_name = "core/anomaly_detail.html"
    context_object_name = "anomaly"
    queryset = Anomaly.objects.detail_page()


class AnomalyCreateView(CreateView):
    model = Anomaly
    template_name = "core/anomaly_form.html"
    fields = ["observation", "flagged_by", "reason", "severity"]
    success_url = reverse_lazy("anomaly-list")


class AnomalyUpdateView(UpdateView):
    model = Anomaly
    template_name = "core/anomaly_form.html"
    fields = ["observation", "flagged_by", "reason", "severity", "resolved", "resolved_notes"]
    success_url = reverse_lazy("anomaly-list")
    queryset = Anomaly.objects.form_page()


class AnomalyDeleteView(DeleteView):
    model = Anomaly
    template_name = "core/anomaly_confirm_delete.html"
    success_url = reverse_lazy("anomaly-list")
    queryset = Anomaly.objects.form_page()

