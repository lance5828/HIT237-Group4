from django import forms

from .models import Observation, Anomaly
from .services import create_observation, flag_anomaly
from .exceptions import ObservationCreateError, AnomalyFlagError


class ObservationCreateForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ["species", "audio_file", "location", "confidence_score", "notes"]

    def save_for_user(self, user):
        try:
            return create_observation(
                user=user,
                species=self.cleaned_data["species"],
                audio_file=self.cleaned_data["audio_file"],
                location=self.cleaned_data["location"],
                confidence_score=self.cleaned_data["confidence_score"],
                notes=self.cleaned_data.get("notes", ""),
            )
        except ObservationCreateError as error:
            raise forms.ValidationError(str(error))


class AnomalyCreateForm(forms.ModelForm):
    class Meta:
        model = Anomaly
        fields = ["observation", "reason", "severity"]

    def save_for_user(self, user):
        try:
            return flag_anomaly(
                user=user,
                observation=self.cleaned_data["observation"],
                reason=self.cleaned_data["reason"],
                severity=self.cleaned_data["severity"],
            )
        except AnomalyFlagError as error:
            raise forms.ValidationError(str(error))