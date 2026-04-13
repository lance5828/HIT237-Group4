from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy

from .models import Species, Observation, Anomaly


def home(request):
    """
    Rendering the home page of the NT Fauna Recordings application.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        HttpResponse: Rendered home.html template.
    """
    return render(request, "core/home.html")

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
    Display a paginated list of all observations recorded in the system.
    
    Attributes:
        model: The Observation model.
        template_name: The template used to render the observation list (core/observation_list.html).
        context_object_name: The variable name for the observations list in the template context.
    """
    model = Observation
    template_name = "core/observation_list.html"
    context_object_name = "observations"


class ObservationDetailView(DetailView):
    """
    Display detailed information about a single observation record.
    
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
    Handle creation of new observation records through a form submission.
    
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
    Display a paginated list of all recorded anomalies in the system.
    
    Anomalies are flagged observations that require further review or investigation.
    
    Attributes:
        model: The Anomaly model.
        template_name: The template used to render the anomaly list (core/anomaly_list.html).
        context_object_name: The variable name for the anomalies list in the template context.
    """
    model = Anomaly
    template_name = "core/anomaly_list.html"
    context_object_name = "anomalies"


class AnomalyDetailView(DetailView):
    """
    Display detailed information about a specific anomaly record.
    
    Shows the anomaly details including the associated observation, who flagged it,
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
    
    Allows users to flag an observation as containing an anomaly and provide
    details such as who flagged it, the reason, and severity level.
    
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