from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .exceptions import ObservationCreateError, AnomalyFlagError
from .forms import ObservationCreateForm, AnomalyCreateForm
from .models import Species, Observation, Anomaly
from .services import create_observation, flag_anomaly


class SpeciesListView(ListView):
    """
    Using the homepage queryset() to filter or annotate relevant species for the landing page.
    Pagination has been used to paginate the list of species on the homepage.
    """
    model = Species
    template_name = "core/species_list.html"
    context_object_name = "species_list"
    paginate_by = 5
    queryset = Species.objects.homepage()


class SpeciesDetailView(DetailView):
    """
    Using the deatil_page() queryset to prefetch related observations or annotations.
    It displays the complete details for a single species.
    """
    model = Species
    template_name = "core/species_detail.html"
    context_object_name = "species"
    queryset = Species.objects.detail_page()


class ObservationListView(ListView):
    """
    Using the list_page() queryset to select related species and user data to avoid N+1 queries.
    Added pagination to display a paginated list of all observations.
    """
    model = Observation
    template_name = "core/observation_list.html"
    context_object_name = "observations"
    paginate_by = 12
    queryset = Observation.objects.list_page()


class ObservationDetailView(DetailView):
    """
    Using the detail_page() queryset to prefetch related anomalies and information about the species.
    DetailView lists the full details for a single observation.
    """
    model = Observation
    template_name = "core/observation_detail.html"
    context_object_name = "observation"
    queryset = Observation.objects.detail_page()


class ObservationCreateView(LoginRequiredMixin, CreateView):
    """
    An authenticated user can create a new observation because of this view.
    It helps delegate business logic to the create_observation() service.
    If there is a service-level failure, it surfaces the error back to the form without raising an unhandled exception. 
    """
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
    """
    Using the form_page() queryset and applying select_related which avoids extra queries when rendering the form.
    Moreover, it allows only authenticated users to update the available observation as LoginRequiredMixin is used. 
    """
    model = Observation
    template_name = "core/observation_form.html"
    fields = ["species", "audio_file", "location", "confidence_score", "notes"]
    success_url = reverse_lazy("observation-list")
    queryset = Observation.objects.form_page()


class ObservationDeleteView(LoginRequiredMixin, DeleteView):
    """
    Using LoginRequiredMixin only allows authenticated users to delete the available observation.
    It also displays a confirmation page before deleting the observation.
    Using the form_page() queryset similar to the UpdateView.
    """
    model = Observation
    template_name = "core/observation_confirm_delete.html"
    success_url = reverse_lazy("observation-list")
    queryset = Observation.objects.form_page()


class AnomalyListView(ListView):
    """
    Using pagination to display a paginated list of all the flagged anomalies.
    Using the list_page() queryset which can select related observations in order to reduce database anomalies.
    """
    model = Anomaly
    template_name = "core/anomaly_list.html"
    context_object_name = "anomalies"
    paginate_by = 12
    queryset = Anomaly.objects.list_page()


class AnomalyDetailView(DetailView):
    """
    Using the detail_page() queryset which can be used to prefetch the related observation and connected species.
    This view displays the complete details for a single anomaly.
    """
    model = Anomaly
    template_name = "core/anomaly_detail.html"
    context_object_name = "anomaly"
    queryset = Anomaly.objects.detail_page()


class AnomalyCreateView(LoginRequiredMixin, CreateView):
    """
    An authenticated user can flag a new anomaly.
    It is used to delegate business logic to the flag_anomaly() service.
    In case of a service-level failure, it surfaces the error back to the form instead of raising an unhandled exception.
    """
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
    """
    It uses LoginRequiredMixin to only allow the authenticated users to update an existing anomaly,
    and resolving it with notes.
    It uses the form_page() queryset for efficiency during form rendering.
    """
    model = Anomaly
    template_name = "core/anomaly_form.html"
    fields = ["observation", "reason", "severity", "resolved", "resolved_notes"]
    success_url = reverse_lazy("anomaly-list")
    queryset = Anomaly.objects.form_page()


class AnomalyDeleteView(LoginRequiredMixin, DeleteView):
    """
    The LoginRequiredMixin allows only authenticated users to delete an existing anomaly.
    It also displays a confirmation page before deleting the anomaly.
    It is using the form_page() queryset which is consistent with the update view.
    """
    model = Anomaly
    template_name = "core/anomaly_confirm_delete.html"
    success_url = reverse_lazy("anomaly-list")
    queryset = Anomaly.objects.form_page()

