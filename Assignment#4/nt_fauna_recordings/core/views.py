from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .exceptions import ObservationCreateError, AnomalyFlagError
from .forms import ObservationCreateForm, AnomalyCreateForm
from .models import Species, Observation, Anomaly
from .services import create_observation, flag_anomaly


class SpeciesListView(ListView):
    model = Species
    template_name = "core/species_list.html"
    context_object_name = "species_list"
    paginate_by = 5
    queryset = Species.objects.homepage()


class SpeciesDetailView(DetailView):
    model = Species
    template_name = "core/species_detail.html"
    context_object_name = "species"
    queryset = Species.objects.detail_page()


class ObservationListView(ListView):
    model = Observation
    template_name = "core/observation_list.html"
    context_object_name = "observations"
    paginate_by = 12
    queryset = Observation.objects.list_page()


class ObservationDetailView(DetailView):
    model = Observation
    template_name = "core/observation_detail.html"
    context_object_name = "observation"
    queryset = Observation.objects.detail_page()


class ObservationCreateView(LoginRequiredMixin, CreateView):
    model = Observation
    form_class = ObservationCreateForm
    template_name = "core/observation_form.html"
    success_url = reverse_lazy("observation-list")

    def form_valid(self, form):
        try:
            create_observation(user=self.request.user, **form.cleaned_data)
            return redirect(self.success_url)
        except ObservationCreateError as error:
            form.add_error(None, str(error))
            return self.form_invalid(form)


class ObservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Observation
    template_name = "core/observation_form.html"
    fields = ["species", "audio_file", "location", "confidence_score", "notes"]
    success_url = reverse_lazy("observation-list")
    queryset = Observation.objects.form_page()


class ObservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Observation
    template_name = "core/observation_confirm_delete.html"
    success_url = reverse_lazy("observation-list")
    queryset = Observation.objects.form_page()


class AnomalyListView(ListView):
    model = Anomaly
    template_name = "core/anomaly_list.html"
    context_object_name = "anomalies"
    paginate_by = 12
    queryset = Anomaly.objects.list_page()


class AnomalyDetailView(DetailView):
    model = Anomaly
    template_name = "core/anomaly_detail.html"
    context_object_name = "anomaly"
    queryset = Anomaly.objects.detail_page()


class AnomalyCreateView(LoginRequiredMixin, CreateView):
    model = Anomaly
    form_class = AnomalyCreateForm
    template_name = "core/anomaly_form.html"
    success_url = reverse_lazy("anomaly-list")

    def form_valid(self, form):
        try:
            flag_anomaly(user=self.request.user, **form.cleaned_data)
            return redirect(self.success_url)
        except AnomalyFlagError as error:
            form.add_error(None, str(error))
            return self.form_invalid(form)


class AnomalyUpdateView(LoginRequiredMixin, UpdateView):
    model = Anomaly
    template_name = "core/anomaly_form.html"
    fields = ["observation", "reason", "severity", "resolved", "resolved_notes"]
    success_url = reverse_lazy("anomaly-list")
    queryset = Anomaly.objects.form_page()


class AnomalyDeleteView(LoginRequiredMixin, DeleteView):
    model = Anomaly
    template_name = "core/anomaly_confirm_delete.html"
    success_url = reverse_lazy("anomaly-list")
    queryset = Anomaly.objects.form_page()

