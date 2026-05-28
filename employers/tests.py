from datetime import date, time

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import resolve, reverse

from accounts.models import User
from employers.forms import EmployerServicePreferenceForm
from employers.models import EmployerLocation, EmployerProfile, EmployerServicePreference, EmployerTrustSignal
from employers.services.onboarding_handoff_service import create_or_update_employer_profile_from_onboarding
from employers.services.profile_completion_service import calculate_employer_profile_completion
from onboarding.models import EmployerOnboardingProfile


class EmployersFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.employer = User.objects.create_user(
            username="employerflow@mk.com",
            email="employerflow@mk.com",
            phone_number="0780000001",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.helper = User.objects.create_user(
            username="helperflow@mk.com",
            email="helperflow@mk.com",
            phone_number="0780000002",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )

    def test_employer_user_can_access_employer_profile_page(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("employers:profile_detail"))
        self.assertIn(response.status_code, [200, 302])

    def test_helper_user_cannot_access_employer_profile_page(self):
        self.client.force_login(self.helper)
        response = self.client.get(reverse("employers:profile_detail"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_anonymous_user_redirects_to_login(self):
        response = self.client.get(reverse("employers:profile_detail"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_employer_profile_preview_loads(self):
        EmployerProfile.objects.create(
            user=self.employer,
            display_name="Zipho L.",
            primary_area="Benoni",
            preferred_contact_method=EmployerProfile.ContactMethod.APP,
            contact_number="0780000001",
        )
        self.client.force_login(self.employer)
        response = self.client.get(reverse("employers:profile_preview"))
        self.assertEqual(response.status_code, 200)

    def test_routes_resolve_correctly(self):
        self.assertEqual(resolve("/employers/profile/").view_name, "employers:profile_detail")
        self.assertEqual(resolve("/employers/profile/edit/").view_name, "employers:profile_edit")
        self.assertEqual(resolve("/employers/profile/locations/").view_name, "employers:locations")
        self.assertEqual(resolve("/employers/profile/preferences/").view_name, "employers:preferences")
        self.assertEqual(resolve("/employers/profile/preview/").view_name, "employers:profile_preview")
        self.assertEqual(resolve("/employers/profile/incomplete/").view_name, "employers:profile_incomplete")


class EmployersHandoffTests(TestCase):
    def setUp(self):
        self.employer = User.objects.create_user(
            username="handoff@mk.com",
            email="handoff@mk.com",
            phone_number="0780000010",
            password="StrongPass123!",
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        EmployerOnboardingProfile.objects.create(
            user=self.employer,
            preferred_location="Benoni",
            service_type="once_off_cleaning",
            service_frequency="weekly",
            preferred_start_date=date.today(),
            preferred_time=time(9, 0),
            special_instructions="Gate code at security",
            is_completed=True,
        )

    def test_employer_profile_can_be_created_from_onboarding_data(self):
        profile = create_or_update_employer_profile_from_onboarding(self.employer)
        self.assertEqual(profile.primary_area, "Benoni")
        self.assertEqual(profile.contact_number, "0780000010")

    def test_handoff_service_is_idempotent(self):
        create_or_update_employer_profile_from_onboarding(self.employer)
        create_or_update_employer_profile_from_onboarding(self.employer)
        self.assertEqual(EmployerProfile.objects.filter(user=self.employer).count(), 1)
        self.assertEqual(EmployerLocation.objects.filter(employer__user=self.employer).count(), 1)
        self.assertEqual(EmployerServicePreference.objects.filter(employer__user=self.employer).count(), 1)
        self.assertEqual(EmployerTrustSignal.objects.filter(employer__user=self.employer).count(), 5)

    def test_onboarding_service_fields_create_update_service_preference(self):
        create_or_update_employer_profile_from_onboarding(self.employer)
        preference = EmployerServicePreference.objects.get(employer__user=self.employer)
        self.assertEqual(preference.service_type, "once_off_cleaning")
        self.assertEqual(preference.service_frequency, "weekly")

    def test_onboarding_location_creates_updates_primary_location(self):
        create_or_update_employer_profile_from_onboarding(self.employer)
        location = EmployerLocation.objects.get(employer__user=self.employer)
        self.assertTrue(location.is_primary)
        self.assertEqual(location.suburb, "Benoni")

    def test_profile_completion_calculation_works(self):
        profile = create_or_update_employer_profile_from_onboarding(self.employer)
        percent = calculate_employer_profile_completion(profile)
        self.assertGreaterEqual(percent, 70)

    def test_duration_validation_prevents_zero_or_negative_duration(self):
        EmployerProfile.objects.create(user=self.employer, display_name="Employer", primary_area="Benoni")
        form = EmployerServicePreferenceForm(
            data={
                "service_type": "once_off_cleaning",
                "service_frequency": "weekly",
                "preferred_day": "MONDAY",
                "preferred_time": "09:00",
                "estimated_duration_hours": 0,
                "special_instructions": "",
            },
            user=self.employer,
        )
        self.assertFalse(form.is_valid())

        valid = EmployerServicePreferenceForm(
            data={
                "service_type": "once_off_cleaning",
                "service_frequency": "weekly",
                "preferred_day": "MONDAY",
                "preferred_time": "09:00",
                "estimated_duration_hours": 3,
                "special_instructions": "",
            },
            user=self.employer,
        )
        self.assertTrue(valid.is_valid())

    def test_findstatic_resolves_employer_assets(self):
        css = finders.find("employers/css/employers.css")
        js = finders.find("employers/js/employers.js")
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertIn("employers\\static\\employers", css)
        self.assertIn("employers\\static\\employers", js)
