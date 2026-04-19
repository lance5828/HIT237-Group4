from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Species, Observation, Anomaly


# -------------------------
# Species Views
# -------------------------

class SpeciesListView(ListView):
    """
    Displaying a paginated list of all species in our database.
    
    Attributes of this:
        model: The Species model.
        The use of template_name: The template used to render the species list (core/species_list.html).
        The use of context_object_name: The variable name for the species list in the template context.
    """
    model = Species
    template_name = "core/species_list.html"
    context_object_name = "species_list"
    paginate_by = 7

class SpeciesDetailView(DetailView):
    """
    Displaying detailed information about a single species.
    
    Attributes:
        model: The Species model.
        template_name: The template used to render the species detail (core/species_detail.html).
        context_object_name: The variable name for the species object in the template context.
    """
    model = Species
    template_name = "core/species_detail.html"
    context_object_name = "species"
    

# -------------------------
# Observation Views
# -------------------------

class ObservationListView(ListView):
    """
    Displaying a paginated list of all observations recorded in the system.
    
    Attributes:
        model: The Observation model.
        template_name: The template used to render the observation list (core/observation_list.html).
        context_object_name: The variable name for the observations list in the template context.
    """
    model = Observation
    template_name = "core/observation_list.html"
    context_object_name = "observations"
    paginate_by = 10

class ObservationDetailView(DetailView):
    """
    Displaying the detailed information about a single observation record.
    
    Attributes:
        model: The Observation model.
        template_name: The template used to render the observation detail (core/observation_detail.html).
        context_object_name: The variable name for the observation object in the template context.
    """
    model = Observation
    template_name = "core/observation_detail.html"
    context_object_name = "observation"


class ObservationCreateView(CreateView):
    """
    Handling the creation of new observation records through a form submission.
    
    Allows users to record a new observation including species identification,
    observer name, audio file, location, confidence score, and notes.
    
    Attributes:
        model: The Observation model.
        template_name: The template used to render the observation form (core/observation_form.html).
        fields: The model fields exposed in the form.
        success_url: The URL to redirect to after successful form submission.
    """
    model = Observation
    template_name = "core/observation_form.html"
    fields = ["species", "observer", "audio_file", "location", "confidence_score", "notes"]
    success_url = reverse_lazy("observation-list")
    
# -------------------------
# Anomaly Views
# -------------------------

class AnomalyListView(ListView):
    """
    Displaying a paginated list of all recorded anomalies in the system.
    
    Anomalies are flagged observations that require further review or investigation.
    
    Attributes:
        model: The Anomaly model.
        template_name: The template used to render the anomaly list (core/anomaly_list.html).
        context_object_name: The variable name for the anomalies list in the template context.
    """
    model = Anomaly
    template_name = "core/anomaly_list.html"
    context_object_name = "anomalies"
    paginate_by = 10

class AnomalyDetailView(DetailView):
    """
    Displaying the detailed information about a specific anomaly record.
    
    Showing the anomaly details including the associated observation, who flagged it,
    reason for flagging, and severity level.
    
    Attributes:
        model: The Anomaly model.
        template_name: The template used to render the anomaly detail (core/anomaly_detail.html).
        context_object_name: The variable name for the anomaly object in the template context.
    """
    model = Anomaly
    template_name = "core/anomaly_detail.html"
    context_object_name = "anomaly"


class AnomalyCreateView(CreateView):
    """
    Handling the creation of new anomaly flags through a form submission.
    
    Allowing our users to flag an observation as containing an anomaly and provide
    details such as who flagged it, the reason, and the severity level.
    
    Attributes:
        model: The Anomaly model.
        template_name: The template used to render the anomaly form (core/anomaly_form.html).
        fields: The model fields exposed in the form.
        success_url: The URL to redirect to after successful form submission.
    """
    model = Anomaly
    template_name = "core/anomaly_form.html"
    fields = ["observation", "flagged_by", "reason", "severity"]
    success_url = reverse_lazy("anomaly-list")

class ObservationUpdateView(UpdateView):
    """
    Handling the updates to an existing observation record through a form submission.

    Attributes:
        model: The Observation model.
        template_name: The template used to render the observation form (core/observation_form.html).
        fields: The model fields exposed in the form.
        success_url: The URL to redirect to after successful form submission.
    """
    model = Observation
    template_name = "core/observation_form.html"  # reusing the same form
    fields = ["species", "observer", "audio_file", "location", "confidence_score", "notes"]
    success_url = reverse_lazy("observation-list")

class ObservationDeleteView(DeleteView):
    """
    Handling the deletion of an existing observation record with a confirmation step.

    Attributes:
        model: The Observation model.
        template_name: The template used to render the deletion confirmation page (core/observation_confirm_delete.html).
        success_url: The URL to redirect to after successful deletion.
    """
    model = Observation
    template_name = "core/observation_confirm_delete.html"
    success_url = reverse_lazy("observation-list")

class AnomalyUpdateView(UpdateView):
    """
    Handling the updates to an existing anomaly record through a form submission.

    Attributes:
        model: The Anomaly model.
        template_name: The template used to render the anomaly form (core/anomaly_form.html).
        fields: The model fields exposed in the form.
        success_url: The URL to redirect to after successful form submission.
    """
    model = Anomaly
    template_name = "core/anomaly_form.html"  # reuse form
    fields = ["observation", "flagged_by", "reason", "severity"]
    success_url = reverse_lazy("anomaly-list")

class AnomalyDeleteView(DeleteView):
    """
    Handling the deletion of an existing anomaly record with a confirmation step.

    Attributes:
        model: The Anomaly model.
        template_name: The template used to render the deletion confirmation page (core/anomaly_confirm_delete.html).
        success_url: The URL to redirect to after successful deletion.
    """
    model = Anomaly
    template_name = "core/anomaly_confirm_delete.html"
    success_url = reverse_lazy("anomaly-list")

