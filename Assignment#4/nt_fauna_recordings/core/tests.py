from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .exceptions import AnomalyFlagError, AnomalyResolveError, ObservationCreateError
from .models import Anomaly, Observation, Species
from .services import create_observation, flag_anomaly, resolve_anomaly


class SpeciesModelTests(TestCase):
	def setUp(self):
		self.species = Species.objects.create(
			category="Mammal",
			common_name="Northern Quoll",
			scientific_name="Dasyurus hallucatus",
			nt_classification=Species.NTClassification.ENDANGERED,
			epbc_classification="Endangered",
			introduced_status="Native",
			order_name="Dasyuromorphia",
			family="Dasyuridae",
		)

	def test_str_returns_common_name_and_scientific_name(self):
		self.assertEqual(str(self.species), "Northern Quoll (Dasyurus hallucatus)")

	def test_display_name_returns_em_dash_format(self):
		self.assertEqual(self.species.display_name(), "Northern Quoll — Dasyurus hallucatus")

	def test_classification_badge_returns_human_readable_label(self):
		self.assertEqual(self.species.classification_badge(), "Endangered")


class ObservationModelTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="observer",
			email="observer@example.com",
			password="password123",
		)
		self.species = Species.objects.create(
			category="Bird",
			common_name="Brolga",
			scientific_name="Antigone rubicunda",
			nt_classification=Species.NTClassification.VULNERABLE,
			epbc_classification="Vulnerable",
			introduced_status="Native",
			order_name="Gruiformes",
			family="Gruidae",
		)
		self.observation_with_notes = Observation.objects.create(
			species=self.species,
			observer=self.user,
			audio_file=SimpleUploadedFile("brolga.wav", b"audio-bytes", content_type="audio/wav"),
			location="Kakadu Wetlands",
			confidence_score=8,
			notes="Large flock observed at dawn.",
		)
		self.observation_without_notes = Observation.objects.create(
			species=self.species,
			observer=self.user,
			audio_file=SimpleUploadedFile("brolga-2.wav", b"audio-bytes", content_type="audio/wav"),
			location="Mary River",
			confidence_score=4,
			notes="",
		)

	def test_str_returns_species_location_and_observer(self):
		expected = f"{self.species.common_name} at {self.observation_with_notes.location} (by {self.user})"
		self.assertEqual(str(self.observation_with_notes), expected)

	def test_has_notes_returns_true_when_notes_exist(self):
		self.assertTrue(self.observation_with_notes.has_notes())

	def test_has_notes_returns_false_when_notes_are_empty(self):
		self.assertFalse(self.observation_without_notes.has_notes())

	def test_confidence_label_returns_high_for_scores_at_least_eight(self):
		self.assertEqual(self.observation_with_notes.confidence_label(), "High")

	def test_confidence_label_returns_moderate_for_scores_at_least_five(self):
		self.observation_without_notes.confidence_score = 5
		self.assertEqual(self.observation_without_notes.confidence_label(), "Moderate")

	def test_confidence_label_returns_low_for_scores_below_five(self):
		self.assertEqual(self.observation_without_notes.confidence_label(), "Low")


class AnomalyModelTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="flagger",
			email="flagger@example.com",
			password="password123",
		)
		self.species = Species.objects.create(
			category="Reptile",
			common_name="Saltwater Crocodile",
			scientific_name="Crocodylus porosus",
			nt_classification=Species.NTClassification.CRITICALLY_ENDANGERED,
			epbc_classification="Protected",
			introduced_status="Native",
			order_name="Crocodilia",
			family="Crocodylidae",
		)
		self.observation = Observation.objects.create(
			species=self.species,
			observer=self.user,
			audio_file=SimpleUploadedFile("croc.wav", b"audio-bytes", content_type="audio/wav"),
			location="East Alligator River",
			confidence_score=9,
			notes="",
		)
		self.anomaly = Anomaly.objects.create(
			observation=self.observation,
			flagged_by=self.user,
			reason="Unexpected movement pattern",
			severity=Anomaly.Severity.HIGH,
			resolved=False,
		)

	def test_str_returns_expected_display(self):
		expected = f"Anomaly on {self.observation} [High]"
		self.assertEqual(str(self.anomaly), expected)

	def test_is_critical_returns_true_only_for_high_unresolved_anomalies(self):
		self.assertTrue(self.anomaly.is_critical())

	def test_is_critical_returns_false_when_resolved_even_if_high(self):
		self.anomaly.resolved = True
		self.assertFalse(self.anomaly.is_critical())


class ServiceTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="serviceuser",
			email="serviceuser@example.com",
			password="password123",
		)
		self.species = Species.objects.create(
			category="Mammal",
			common_name="Dingo",
			scientific_name="Canis dingo",
			nt_classification=Species.NTClassification.VULNERABLE,
			epbc_classification="Vulnerable",
			introduced_status="Native",
			order_name="Carnivora",
			family="Canidae",
		)
		self.observation = Observation.objects.create(
			species=self.species,
			observer=self.user,
			audio_file=SimpleUploadedFile("dingo.wav", b"audio-bytes", content_type="audio/wav"),
			location="Litchfield National Park",
			confidence_score=7,
			notes="",
		)
		self.anomaly = Anomaly.objects.create(
			observation=self.observation,
			flagged_by=self.user,
			reason="Initial reason",
			severity=Anomaly.Severity.MEDIUM,
			resolved=False,
		)
		self.valid_audio = SimpleUploadedFile("service-observation.wav", b"audio-bytes", content_type="audio/wav")

	def test_create_observation_creates_observation_successfully(self):
		observation = create_observation(
			user=self.user,
			species=self.species,
			audio_file=self.valid_audio,
			location="Katherine Gorge",
			confidence_score=9,
			notes="Seen near water.",
		)

		self.assertEqual(observation.species, self.species)
		self.assertEqual(observation.observer, self.user)
		self.assertEqual(observation.location, "Katherine Gorge")
		self.assertEqual(observation.confidence_score, 9)
		self.assertEqual(observation.notes, "Seen near water.")
		self.assertEqual(Observation.objects.count(), 2)

	def test_create_observation_raises_error_when_user_is_not_authenticated(self):
		with self.assertRaises(ObservationCreateError):
			create_observation(
				user=AnonymousUser(),
				species=self.species,
				audio_file=self.valid_audio,
				location="Katherine Gorge",
				confidence_score=9,
			)

	def test_create_observation_raises_error_when_location_is_blank_or_empty(self):
		for location in ["", "   "]:
			with self.subTest(location=location):
				with self.assertRaises(ObservationCreateError):
					create_observation(
						user=self.user,
						species=self.species,
						audio_file=self.valid_audio,
						location=location,
						confidence_score=9,
					)

	def test_create_observation_raises_error_when_confidence_score_is_outside_range(self):
		for confidence_score in [0, 11]:
			with self.subTest(confidence_score=confidence_score):
				with self.assertRaises(ObservationCreateError):
					create_observation(
						user=self.user,
						species=self.species,
						audio_file=self.valid_audio,
						location="Katherine Gorge",
						confidence_score=confidence_score,
					)

	def test_flag_anomaly_creates_anomaly_successfully(self):
		anomaly = flag_anomaly(
			user=self.user,
			observation=self.observation,
			reason="Observed outside known range.",
			severity=Anomaly.Severity.HIGH,
		)

		self.assertEqual(anomaly.observation, self.observation)
		self.assertEqual(anomaly.flagged_by, self.user)
		self.assertEqual(anomaly.reason, "Observed outside known range.")
		self.assertEqual(anomaly.severity, Anomaly.Severity.HIGH)
		self.assertFalse(anomaly.resolved)

	def test_flag_anomaly_raises_error_when_user_is_not_authenticated(self):
		with self.assertRaises(AnomalyFlagError):
			flag_anomaly(
				user=AnonymousUser(),
				observation=self.observation,
				reason="Observed outside known range.",
				severity=Anomaly.Severity.HIGH,
			)

	def test_flag_anomaly_raises_error_when_reason_is_blank_or_empty(self):
		for reason in ["", "   "]:
			with self.subTest(reason=reason):
				with self.assertRaises(AnomalyFlagError):
					flag_anomaly(
						user=self.user,
						observation=self.observation,
						reason=reason,
						severity=Anomaly.Severity.HIGH,
					)

	def test_resolve_anomaly_sets_resolved_and_notes(self):
		resolved_anomaly = resolve_anomaly(
			user=self.user,
			anomaly=self.anomaly,
			resolved_notes="Reviewed and confirmed.",
		)

		resolved_anomaly.refresh_from_db()
		self.assertTrue(resolved_anomaly.resolved)
		self.assertEqual(resolved_anomaly.resolved_notes, "Reviewed and confirmed.")

	def test_resolve_anomaly_raises_error_when_user_is_not_authenticated(self):
		with self.assertRaises(AnomalyResolveError):
			resolve_anomaly(
				user=AnonymousUser(),
				anomaly=self.anomaly,
				resolved_notes="Reviewed and confirmed.",
			)

	def test_resolve_anomaly_raises_error_when_already_resolved(self):
		self.anomaly.resolved = True
		self.anomaly.save(update_fields=["resolved"])

		with self.assertRaises(AnomalyResolveError):
			resolve_anomaly(
				user=self.user,
				anomaly=self.anomaly,
				resolved_notes="Reviewed and confirmed.",
			)


class ViewTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="viewer",
			email="viewer@example.com",
			password="password123",
		)
		self.species = Species.objects.create(
			category="Bird",
			common_name="Magpie Goose",
			scientific_name="Anseranas semipalmata",
			nt_classification=Species.NTClassification.VULNERABLE,
			epbc_classification="Vulnerable",
			introduced_status="Native",
			order_name="Anseriformes",
			family="Anseranatidae",
		)
		self.observation = Observation.objects.create(
			species=self.species,
			observer=self.user,
			audio_file=SimpleUploadedFile("goose.wav", b"audio-bytes", content_type="audio/wav"),
			location="Fogg Dam",
			confidence_score=8,
			notes="Large group near the billabong.",
		)
		self.anomaly = Anomaly.objects.create(
			observation=self.observation,
			flagged_by=self.user,
			reason="Large flock in unusual season.",
			severity=Anomaly.Severity.MEDIUM,
			resolved=False,
		)
		self.client.force_login(self.user)

	def test_get_species_list_returns_200(self):
		response = self.client.get("/species/")
		self.assertEqual(response.status_code, 200)

	def test_get_species_detail_returns_200(self):
		response = self.client.get(f"/species/{self.species.pk}/")
		self.assertEqual(response.status_code, 200)

	def test_get_observation_list_returns_200(self):
		response = self.client.get("/observations/")
		self.assertEqual(response.status_code, 200)

	def test_get_observation_detail_returns_200(self):
		response = self.client.get(f"/observations/{self.observation.pk}/")
		self.assertEqual(response.status_code, 200)

	def test_get_anomaly_list_returns_200(self):
		response = self.client.get("/anomalies/")
		self.assertEqual(response.status_code, 200)

	def test_get_anomaly_detail_returns_200(self):
		response = self.client.get(f"/anomalies/{self.anomaly.pk}/")
		self.assertEqual(response.status_code, 200)

	def test_post_observation_create_redirects_to_observation_list(self):
		response = self.client.post(
			"/observations/create/",
			data={
				"species": self.species.pk,
				"audio_file": SimpleUploadedFile("new-observation.wav", b"audio-bytes", content_type="audio/wav"),
				"location": "Arnhem Land",
				"confidence_score": 8,
				"notes": "Seen at dusk.",
			},
		)

		self.assertRedirects(response, reverse("observation-list"))

	def test_post_anomaly_create_redirects_to_anomaly_list(self):
		response = self.client.post(
			"/anomalies/create/",
			data={
				"observation": self.observation.pk,
				"reason": "Unusual activity detected.",
				"severity": Anomaly.Severity.HIGH,
			},
		)

		self.assertRedirects(response, reverse("anomaly-list"))


class PermissionBoundaryTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(
			username="boundary",
			email="boundary@example.com",
			password="password123",
		)
		self.species = Species.objects.create(
			category="Bird",
			common_name="Black Kite",
			scientific_name="Milvus migrans",
			nt_classification=Species.NTClassification.VULNERABLE,
			epbc_classification="Vulnerable",
			introduced_status="Native",
			order_name="Accipitriformes",
			family="Accipitridae",
		)
		self.observation = Observation.objects.create(
			species=self.species,
			observer=self.user,
			audio_file=SimpleUploadedFile("kite.wav", b"audio-bytes", content_type="audio/wav"),
			location="Darwin Harbour",
			confidence_score=6,
			notes="",
		)

	def test_unauthenticated_post_observation_create_redirects_to_login(self):
		response = self.client.post(
			"/observations/create/",
			data={
				"species": self.species.pk,
				"audio_file": SimpleUploadedFile("anon-observation.wav", b"audio-bytes", content_type="audio/wav"),
				"location": "Kakadu",
				"confidence_score": 7,
				"notes": "",
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertIn("/accounts/login/", response["Location"])

	def test_unauthenticated_post_anomaly_create_redirects_to_login(self):
		response = self.client.post(
			"/anomalies/create/",
			data={
				"observation": self.observation.pk,
				"reason": "Suspected anomaly.",
				"severity": Anomaly.Severity.LOW,
			},
		)

		self.assertEqual(response.status_code, 302)
		self.assertIn("/accounts/login/", response["Location"])

	def test_unauthenticated_get_observation_create_redirects_to_login(self):
		response = self.client.get("/observations/create/")
		self.assertEqual(response.status_code, 302)
		self.assertIn("/accounts/login/", response["Location"])

	def test_unauthenticated_get_anomaly_create_redirects_to_login(self):
		response = self.client.get("/anomalies/create/")
		self.assertEqual(response.status_code, 302)
		self.assertIn("/accounts/login/", response["Location"])
