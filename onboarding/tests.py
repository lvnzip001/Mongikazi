from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from locations.models import Locality
from onboarding.forms import EmployerServiceForm, HelperProfileForm
from onboarding.models import EmployerOnboardingProfile, HelperOnboardingProfile


class OnboardingFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.employer = User.objects.create_user(
            username="employer@mk.com",
            email="employer@mk.com",
            password=self.password,
            role=User.Role.EMPLOYER,
            phone_number="0711111111",
            is_onboarding_complete=False,
        )
        self.helper = User.objects.create_user(
            username="helper@mk.com",
            email="helper@mk.com",
            password=self.password,
            role=User.Role.HELPER,
            phone_number="0722222222",
            is_onboarding_complete=False,
        )

    def test_unauthenticated_user_redirected_from_onboarding_start_to_login(self):
        response = self.client.get(reverse("onboarding:start"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_employer_routed_to_employer_onboarding(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("onboarding:start"))
        self.assertRedirects(response, reverse("onboarding:employer_service"), fetch_redirect_response=False)

    def test_helper_routed_to_helper_onboarding(self):
        self.client.force_login(self.helper)
        response = self.client.get(reverse("onboarding:start"))
        self.assertRedirects(response, reverse("onboarding:helper_profile"), fetch_redirect_response=False)

    def test_employer_cannot_access_helper_onboarding_steps(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("onboarding:helper_profile"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_helper_cannot_access_employer_onboarding_steps(self):
        self.client.force_login(self.helper)
        response = self.client.get(reverse("onboarding:employer_service"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_employer_onboarding_completion_sets_flags(self):
        benoni = Locality.objects.create(
            name="Benoni",
            province="Gauteng",
            slug="benoni-gauteng-employer",
            municipality="Ekurhuleni",
            locality_type=Locality.LocalityType.SUBURB,
        )
        self.client.force_login(self.employer)
        self.client.post(
            reverse("onboarding:employer_service"),
            {"service_type": "once_off_cleaning", "service_frequency": "weekly"},
        )
        self.client.post(
            reverse("onboarding:employer_location"),
            {
                "preferred_location_query": "Benoni, Gauteng",
                "preferred_location_locality_id": benoni.pk,
                "preferred_start_date": date.today().isoformat(),
                "preferred_time": time(8, 0).isoformat(timespec="minutes"),
                "special_instructions": "Please ring the bell.",
            },
        )
        response = self.client.post(reverse("onboarding:employer_complete"))

        profile = EmployerOnboardingProfile.objects.get(user=self.employer)
        self.employer.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(profile.is_completed)
        self.assertIsNotNone(profile.completed_at)
        self.assertTrue(self.employer.is_onboarding_complete)

    def test_helper_onboarding_completion_sets_flags(self):
        benoni = Locality.objects.create(
            name="Benoni",
            province="Gauteng",
            slug="benoni-gauteng",
            municipality="Ekurhuleni",
            locality_type=Locality.LocalityType.SUBURB,
        )
        self.client.force_login(self.helper)
        self.client.post(
            reverse("onboarding:helper_profile"),
            {
                "display_name": "Nomsa",
                "location_query": "Benoni, Gauteng",
                "location_locality_id": benoni.pk,
                "years_experience": 4,
                "bio": "Reliable and punctual helper.",
            },
        )
        self.client.post(
            reverse("onboarding:helper_services"),
            {
                "selected_categories": ["cleaning", "laundry"],
                "work_area_query": "Benoni, Gauteng",
                "work_area_locality_id": benoni.pk,
                "availability_summary": "08:00 to 16:00",
            },
        )
        response = self.client.post(
            reverse("onboarding:helper_trust"),
            {
                "has_id_document_ready": "True",
                "has_criminal_check_ready": "False",
                "has_references": "True",
            },
        )
        self.assertRedirects(response, reverse("onboarding:helper_complete"), fetch_redirect_response=False)
        self.client.post(reverse("onboarding:helper_complete"))

        profile = HelperOnboardingProfile.objects.get(user=self.helper)
        self.assertEqual(profile.preferred_work_area, "Benoni, Gauteng")
        self.assertEqual(profile.preferred_work_area_locality_id, benoni.pk)
        self.assertEqual(profile.availability_summary, "08:00 to 16:00")
        self.helper.refresh_from_db()
        self.assertTrue(profile.is_completed)
        self.assertIsNotNone(profile.completed_at)
        self.assertTrue(self.helper.is_onboarding_complete)

    def test_employer_location_accepts_query_without_hidden_id_when_label_matches(self):
        east_london = Locality.objects.create(
            name="East London",
            province="Eastern Cape",
            slug="east-london-ec-employer",
            municipality="Buffalo City",
            locality_type=Locality.LocalityType.CITY,
        )
        self.client.force_login(self.employer)
        self.client.post(
            reverse("onboarding:employer_service"),
            {"service_type": "once_off_cleaning", "service_frequency": "weekly"},
        )
        response = self.client.post(
            reverse("onboarding:employer_location"),
            {
                "preferred_location_query": east_london.display_label,
                "preferred_start_date": date.today().isoformat(),
                "preferred_time": time(8, 0).isoformat(timespec="minutes"),
                "special_instructions": "Ring the bell.",
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = EmployerOnboardingProfile.objects.get(user=self.employer)
        self.assertEqual(profile.preferred_location_locality_id, east_london.pk)

    def test_helper_services_accepts_work_area_carried_from_step_one_location(self):
        east_london = Locality.objects.create(
            name="East London",
            province="Eastern Cape",
            slug="east-london-ec",
            municipality="Buffalo City",
            locality_type=Locality.LocalityType.CITY,
        )
        self.client.force_login(self.helper)
        self.client.post(
            reverse("onboarding:helper_profile"),
            {
                "display_name": "Thandi",
                "location_query": east_london.display_label,
                "location_locality_id": east_london.pk,
                "years_experience": 3,
                "bio": "Experienced helper.",
            },
        )
        response = self.client.post(
            reverse("onboarding:helper_services"),
            {
                "selected_categories": ["cleaning"],
                "work_area_query": east_london.display_label,
                "availability_summary": "08:00 to 16:00",
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = HelperOnboardingProfile.objects.get(user=self.helper)
        self.assertEqual(profile.preferred_work_area_locality_id, east_london.pk)

    def test_forms_validate_required_fields(self):
        employer_form = EmployerServiceForm(data={})
        helper_form = HelperProfileForm(data={})
        self.assertFalse(employer_form.is_valid())
        self.assertFalse(helper_form.is_valid())

    def test_onboarding_start_redirects_completed_users_appropriately(self):
        self.employer.is_onboarding_complete = True
        self.employer.save(update_fields=["is_onboarding_complete"])
        self.client.force_login(self.employer)

        response = self.client.get(reverse("onboarding:start"))
        self.assertRedirects(response, reverse("accounts:account_pending"), fetch_redirect_response=False)

    def test_account_login_redirect_sends_incomplete_users_to_onboarding_start(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"identifier": self.employer.email, "password": self.password},
        )
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)
