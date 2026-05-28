from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .exceptions import (
    AnomalyFlagError,
    AnomalyResolveError,
    ObservationCreateError,
    ServiceError,
)
from .models import Anomaly, Observation, Species
from .services import create_observation, flag_anomaly, resolve_anomaly


class TestDataMixin:
    def create_user(self, username="user"):
        User = get_user_model()
        count = User.objects.count() + 1
        unique_username = f"{username}_{count}"

        return User.objects.create_user(
            username=unique_username,
            email=f"{unique_username}@example.com",
            password="password123",
        )

    def create_audio(self, name="test.wav"):
        return SimpleUploadedFile(
            name,
            b"audio-bytes",
            content_type="audio/wav",
        )

    def create_species(
        self,
        common_name="Northern Quoll",
        scientific_name="Dasyurus hallucatus",
        category="Mammal",
        classification=Species.NTClassification.ENDANGERED,
    ):
        count = Species.objects.count() + 1
        unique_scientific_name = f"{scientific_name} {count}"

        return Species.objects.create(
            category=category,
            common_name=common_name,
            scientific_name=unique_scientific_name,
            nt_classification=classification,
            epbc_classification="Endangered",
            introduced_status="Native",
            order_name="Test Order",
            family="Test Family",
        )

    def create_observation(self, user=None, species=None, **kwargs):
        user = user or self.create_user("observer")
        species = species or self.create_species()

        return Observation.objects.create(
            species=species,
            observer=user,
            audio_file=self.create_audio(kwargs.get("audio_name", "observation.wav")),
            location=kwargs.get("location", "Kakadu"),
            confidence_score=kwargs.get("confidence_score", 8),
            notes=kwargs.get("notes", ""),
        )

    def create_anomaly(self, user=None, observation=None, **kwargs):
        user = user or self.create_user("flagger")
        observation = observation or self.create_observation(user=user)

        return Anomaly.objects.create(
            observation=observation,
            flagged_by=user,
            reason=kwargs.get("reason", "Unusual sound pattern."),
            severity=kwargs.get("severity", Anomaly.Severity.MEDIUM),
            resolved=kwargs.get("resolved", False),
            resolved_notes=kwargs.get("resolved_notes", ""),
        )


class ExceptionHierarchyTests(TestCase):
    def test_service_exceptions_inherit_from_service_error(self):
        self.assertTrue(issubclass(ObservationCreateError, ServiceError))
        self.assertTrue(issubclass(AnomalyFlagError, ServiceError))
        self.assertTrue(issubclass(AnomalyResolveError, ServiceError))


class ModelBehaviourTests(TestDataMixin, TestCase):
    def test_species_display_helpers_return_readable_text(self):
        species = self.create_species(
            common_name="Northern Quoll",
            scientific_name="Dasyurus hallucatus",
        )

        self.assertIn("Northern Quoll", str(species))
        self.assertIn("Dasyurus hallucatus", str(species))
        self.assertIn("Northern Quoll", species.display_name())
        self.assertIn("Dasyurus hallucatus", species.display_name())
        self.assertEqual(species.classification_badge(), "Endangered")

    def test_observation_confidence_label_behaviour(self):
        user = self.create_user("confidence_user")
        species = self.create_species(
            common_name="Brolga",
            scientific_name="Antigone rubicunda",
            category="Bird",
            classification=Species.NTClassification.VULNERABLE,
        )

        high = self.create_observation(
            user=user,
            species=species,
            confidence_score=8,
            audio_name="high.wav",
        )
        moderate = self.create_observation(
            user=user,
            species=species,
            confidence_score=5,
            audio_name="moderate.wav",
        )
        low = self.create_observation(
            user=user,
            species=species,
            confidence_score=3,
            audio_name="low.wav",
        )

        self.assertEqual(high.confidence_label(), "High")
        self.assertEqual(moderate.confidence_label(), "Moderate")
        self.assertEqual(low.confidence_label(), "Low")

    def test_observation_has_notes_behaviour(self):
        user = self.create_user("notes_user")
        species = self.create_species(
            common_name="Magpie Goose",
            scientific_name="Anseranas semipalmata",
            category="Bird",
            classification=Species.NTClassification.VULNERABLE,
        )

        with_notes = self.create_observation(
            user=user,
            species=species,
            notes="Useful note.",
            audio_name="with-notes.wav",
        )
        without_notes = self.create_observation(
            user=user,
            species=species,
            notes="",
            audio_name="without-notes.wav",
        )

        self.assertTrue(with_notes.has_notes())
        self.assertFalse(without_notes.has_notes())

    def test_anomaly_is_critical_only_when_high_and_unresolved(self):
        anomaly = self.create_anomaly(
            severity=Anomaly.Severity.HIGH,
            resolved=False,
        )

        self.assertTrue(anomaly.is_critical())

        anomaly.resolved = True
        self.assertFalse(anomaly.is_critical())


class QuerySetTests(TestDataMixin, TestCase):
    def test_species_homepage_returns_threatened_species_ordered_for_homepage(self):
        vulnerable = self.create_species(
            common_name="Brolga",
            scientific_name="Antigone rubicunda",
            category="Bird",
            classification=Species.NTClassification.VULNERABLE,
        )
        endangered = self.create_species(
            common_name="Dingo",
            scientific_name="Canis dingo",
            category="Mammal",
            classification=Species.NTClassification.ENDANGERED,
        )

        queryset = Species.objects.homepage()

        self.assertIn(vulnerable, queryset)
        self.assertIn(endangered, queryset)
        self.assertEqual(
            list(queryset),
            list(queryset.order_by("category", "common_name", "scientific_name")),
        )

    def test_species_search_by_name_finds_common_or_scientific_name(self):
        species = self.create_species(
            common_name="Black-footed Tree-rat",
            scientific_name="Mesembriomys gouldii",
        )

        self.assertIn(species, Species.objects.search_by_name("Tree-rat"))
        self.assertIn(species, Species.objects.search_by_name("gouldii"))

    def test_observation_with_notes_returns_only_observations_with_notes(self):
        user = self.create_user("query_notes_user")
        species = self.create_species(
            common_name="Red Goshawk",
            scientific_name="Erythrotriorchis radiatus",
            category="Bird",
            classification=Species.NTClassification.ENDANGERED,
        )

        with_notes = self.create_observation(
            user=user,
            species=species,
            notes="Recorded near river.",
            audio_name="query-with-notes.wav",
        )
        without_notes = self.create_observation(
            user=user,
            species=species,
            notes="",
            audio_name="query-no-notes.wav",
        )

        queryset = Observation.objects.with_notes()

        self.assertIn(with_notes, queryset)
        self.assertNotIn(without_notes, queryset)

    def test_observation_high_confidence_returns_scores_above_threshold(self):
        user = self.create_user("query_confidence_user")
        species = self.create_species(
            common_name="Masked Owl",
            scientific_name="Tyto novaehollandiae",
            category="Bird",
            classification=Species.NTClassification.VULNERABLE,
        )

        high = self.create_observation(
            user=user,
            species=species,
            confidence_score=9,
            audio_name="query-high.wav",
        )
        low = self.create_observation(
            user=user,
            species=species,
            confidence_score=4,
            audio_name="query-low.wav",
        )

        queryset = Observation.objects.high_confidence()

        self.assertIn(high, queryset)
        self.assertNotIn(low, queryset)

    def test_anomaly_critical_returns_high_unresolved_only(self):
        user = self.create_user("critical_user")
        species = self.create_species(
            common_name="Northern Brushtail Possum",
            scientific_name="Trichosurus arnhemensis",
            category="Mammal",
            classification=Species.NTClassification.VULNERABLE,
        )

        observation_one = self.create_observation(
            user=user,
            species=species,
            audio_name="critical-one.wav",
        )
        observation_two = self.create_observation(
            user=user,
            species=species,
            audio_name="critical-two.wav",
        )
        observation_three = self.create_observation(
            user=user,
            species=species,
            audio_name="critical-three.wav",
        )

        critical = self.create_anomaly(
            user=user,
            observation=observation_one,
            severity=Anomaly.Severity.HIGH,
            resolved=False,
            reason="Critical unresolved.",
        )
        resolved_high = self.create_anomaly(
            user=user,
            observation=observation_two,
            severity=Anomaly.Severity.HIGH,
            resolved=True,
            reason="Resolved high.",
        )
        medium = self.create_anomaly(
            user=user,
            observation=observation_three,
            severity=Anomaly.Severity.MEDIUM,
            resolved=False,
            reason="Medium issue.",
        )

        queryset = Anomaly.objects.critical()

        self.assertIn(critical, queryset)
        self.assertNotIn(resolved_high, queryset)
        self.assertNotIn(medium, queryset)


class ServiceTests(TestDataMixin, TestCase):
    def setUp(self):
        self.user = self.create_user("serviceuser")
        self.species = self.create_species(
            common_name="Dingo",
            scientific_name="Canis dingo",
            category="Mammal",
            classification=Species.NTClassification.VULNERABLE,
        )
        self.observation = self.create_observation(
            user=self.user,
            species=self.species,
            audio_name="service-observation.wav",
        )
        self.anomaly = self.create_anomaly(
            user=self.user,
            observation=self.observation,
            reason="Initial reason.",
        )

    def test_create_observation_creates_record_and_assigns_user(self):
        observation = create_observation(
            user=self.user,
            species=self.species,
            audio_file=self.create_audio("new.wav"),
            location="Katherine Gorge",
            confidence_score=9,
            notes="Seen near water.",
        )

        self.assertEqual(observation.observer, self.user)
        self.assertEqual(observation.species, self.species)
        self.assertEqual(observation.location, "Katherine Gorge")
        self.assertEqual(observation.confidence_score, 9)

    def test_create_observation_rejects_anonymous_user_and_does_not_create_record(self):
        before_count = Observation.objects.count()

        with self.assertRaises(ObservationCreateError):
            create_observation(
                user=AnonymousUser(),
                species=self.species,
                audio_file=self.create_audio("anon.wav"),
                location="Kakadu",
                confidence_score=8,
            )

        self.assertEqual(Observation.objects.count(), before_count)

    def test_create_observation_rejects_invalid_confidence_score(self):
        before_count = Observation.objects.count()

        with self.assertRaises(ObservationCreateError):
            create_observation(
                user=self.user,
                species=self.species,
                audio_file=self.create_audio("bad.wav"),
                location="Kakadu",
                confidence_score=11,
            )

        self.assertEqual(Observation.objects.count(), before_count)

    def test_create_observation_rejects_blank_location(self):
        before_count = Observation.objects.count()

        with self.assertRaises(ObservationCreateError):
            create_observation(
                user=self.user,
                species=self.species,
                audio_file=self.create_audio("blank-location.wav"),
                location="   ",
                confidence_score=8,
            )

        self.assertEqual(Observation.objects.count(), before_count)

    def test_flag_anomaly_creates_record_and_assigns_flagging_user(self):
        anomaly = flag_anomaly(
            user=self.user,
            observation=self.observation,
            reason="Observed outside expected area.",
            severity=Anomaly.Severity.HIGH,
        )

        self.assertEqual(anomaly.flagged_by, self.user)
        self.assertEqual(anomaly.observation, self.observation)
        self.assertEqual(anomaly.severity, Anomaly.Severity.HIGH)
        self.assertFalse(anomaly.resolved)

    def test_flag_anomaly_rejects_blank_reason_and_does_not_create_record(self):
        before_count = Anomaly.objects.count()

        with self.assertRaises(AnomalyFlagError):
            flag_anomaly(
                user=self.user,
                observation=self.observation,
                reason="   ",
                severity=Anomaly.Severity.LOW,
            )

        self.assertEqual(Anomaly.objects.count(), before_count)

    def test_flag_anomaly_rejects_anonymous_user(self):
        before_count = Anomaly.objects.count()

        with self.assertRaises(AnomalyFlagError):
            flag_anomaly(
                user=AnonymousUser(),
                observation=self.observation,
                reason="Anonymous flag attempt.",
                severity=Anomaly.Severity.LOW,
            )

        self.assertEqual(Anomaly.objects.count(), before_count)

    def test_resolve_anomaly_marks_anomaly_as_resolved(self):
        resolved = resolve_anomaly(
            user=self.user,
            anomaly=self.anomaly,
            resolved_notes="Reviewed by staff.",
        )

        resolved.refresh_from_db()
        self.assertTrue(resolved.resolved)
        self.assertEqual(resolved.resolved_notes, "Reviewed by staff.")

    def test_resolve_anomaly_rejects_already_resolved_anomaly(self):
        self.anomaly.resolved = True
        self.anomaly.save(update_fields=["resolved"])

        with self.assertRaises(AnomalyResolveError):
            resolve_anomaly(
                user=self.user,
                anomaly=self.anomaly,
                resolved_notes="Trying again.",
            )


class ViewIntegrationTests(TestDataMixin, TestCase):
    def setUp(self):
        self.user = self.create_user("viewer")
        self.species = self.create_species(
            common_name="Magpie Goose",
            scientific_name="Anseranas semipalmata",
            category="Bird",
            classification=Species.NTClassification.VULNERABLE,
        )
        self.observation = self.create_observation(
            user=self.user,
            species=self.species,
            location="Fogg Dam",
            confidence_score=8,
            notes="Large group near the billabong.",
            audio_name="view-observation.wav",
        )
        self.anomaly = self.create_anomaly(
            user=self.user,
            observation=self.observation,
            reason="Large flock in unusual season.",
            severity=Anomaly.Severity.MEDIUM,
        )
        self.client.force_login(self.user)

    def test_list_detail_edit_and_delete_pages_load_using_named_urls(self):
        urls = [
            reverse("species-list"),
            reverse("species-detail", args=[self.species.pk]),
            reverse("observation-list"),
            reverse("observation-detail", args=[self.observation.pk]),
            reverse("observation-edit", args=[self.observation.pk]),
            reverse("observation-delete", args=[self.observation.pk]),
            reverse("anomaly-list"),
            reverse("anomaly-detail", args=[self.anomaly.pk]),
            reverse("anomaly-edit", args=[self.anomaly.pk]),
            reverse("anomaly-delete", args=[self.anomaly.pk]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_observation_create_view_creates_observation_for_logged_in_user(self):
        response = self.client.post(
            reverse("observation-create"),
            data={
                "species": self.species.pk,
                "audio_file": self.create_audio("view-created.wav"),
                "location": "Arnhem Land",
                "confidence_score": 8,
                "notes": "Created through view.",
            },
        )

        self.assertRedirects(response, reverse("observation-list"))

        observation = Observation.objects.get(location="Arnhem Land")
        self.assertEqual(observation.observer, self.user)

    def test_anomaly_create_view_creates_anomaly_for_logged_in_user(self):
        response = self.client.post(
            reverse("anomaly-create"),
            data={
                "observation": self.observation.pk,
                "reason": "Unusual activity detected.",
                "severity": Anomaly.Severity.HIGH,
            },
        )

        self.assertRedirects(response, reverse("anomaly-list"))

        anomaly = Anomaly.objects.get(reason="Unusual activity detected.")
        self.assertEqual(anomaly.flagged_by, self.user)

    def test_invalid_observation_create_returns_form_error_not_500(self):
        before_count = Observation.objects.count()

        response = self.client.post(
            reverse("observation-create"),
            data={
                "species": self.species.pk,
                "audio_file": self.create_audio("invalid.wav"),
                "location": "Kakadu",
                "confidence_score": 99,
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Observation.objects.count(), before_count)
        self.assertContains(response, "Confidence")

    def test_invalid_anomaly_create_returns_form_error_not_500(self):
        before_count = Anomaly.objects.count()

        response = self.client.post(
            reverse("anomaly-create"),
            data={
                "observation": self.observation.pk,
                "reason": "",
                "severity": Anomaly.Severity.HIGH,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Anomaly.objects.count(), before_count)


class PermissionBoundaryTests(TestDataMixin, TestCase):
    def setUp(self):
        self.user = self.create_user("owner")
        self.species = self.create_species(
            common_name="Black Kite",
            scientific_name="Milvus migrans",
            category="Bird",
            classification=Species.NTClassification.VULNERABLE,
        )
        self.observation = self.create_observation(
            user=self.user,
            species=self.species,
            location="Darwin Harbour",
            confidence_score=6,
            notes="",
            audio_name="permission-observation.wav",
        )
        self.anomaly = self.create_anomaly(
            user=self.user,
            observation=self.observation,
            reason="Permission boundary anomaly.",
        )

    def test_anonymous_user_cannot_access_create_edit_or_delete_pages(self):
        protected_urls = [
            reverse("observation-create"),
            reverse("observation-edit", args=[self.observation.pk]),
            reverse("observation-delete", args=[self.observation.pk]),
            reverse("anomaly-create"),
            reverse("anomaly-edit", args=[self.anomaly.pk]),
            reverse("anomaly-delete", args=[self.anomaly.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response["Location"])

    def test_anonymous_user_cannot_post_create_actions(self):
        observation_response = self.client.post(
            reverse("observation-create"),
            data={
                "species": self.species.pk,
                "audio_file": self.create_audio("anon.wav"),
                "location": "Kakadu",
                "confidence_score": 7,
                "notes": "",
            },
        )

        anomaly_response = self.client.post(
            reverse("anomaly-create"),
            data={
                "observation": self.observation.pk,
                "reason": "Anonymous flag attempt.",
                "severity": Anomaly.Severity.LOW,
            },
        )

        self.assertEqual(observation_response.status_code, 302)
        self.assertEqual(anomaly_response.status_code, 302)
        self.assertIn("/accounts/login/", observation_response["Location"])
        self.assertIn("/accounts/login/", anomaly_response["Location"])
