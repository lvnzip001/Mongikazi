from datetime import time

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse, resolve

from accounts.models import User
from helpers.forms import HelperAvailabilityForm
from helpers.models import HelperProfile, HelperSkill, HelperTrustSignal, ServiceCategory
from helpers.services.onboarding_handoff_service import (
    create_or_update_helper_profile_from_onboarding,
    ensure_default_service_categories,
)
from helpers.services.profile_completion_service import calculate_helper_profile_completion
from onboarding.models import HelperOnboardingProfile


class HelpersFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.helper = User.objects.create_user(
            username="helperflow@mk.com",
            email="helperflow@mk.com",
            phone_number="0760000001",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.employer = User.objects.create_user(
            username="employerflow@mk.com",
            email="employerflow@mk.com",
            phone_number="0760000002",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )

    def test_helper_user_can_access_helper_profile_page(self):
        self.client.force_login(self.helper)
        response = self.client.get(reverse("helpers:profile_detail"))
        self.assertIn(response.status_code, [200, 302])

    def test_employer_user_cannot_access_helper_profile_page(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("helpers:profile_detail"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_anonymous_user_redirects_to_login(self):
        response = self.client.get(reverse("helpers:profile_detail"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_availability_validation_prevents_end_time_before_start_time(self):
        form = HelperAvailabilityForm(
            data={"day_of_week": "MONDAY", "start_time": "12:00", "end_time": "08:00", "is_available": True}
        )
        self.assertFalse(form.is_valid())

    def test_helper_profile_preview_loads(self):
        HelperProfile.objects.create(user=self.helper, display_name="Nomsa", location="Benoni")
        self.client.force_login(self.helper)
        response = self.client.get(reverse("helpers:profile_preview"))
        self.assertEqual(response.status_code, 200)

    def test_routes_resolve_correctly(self):
        self.assertEqual(resolve("/helpers/profile/").view_name, "helpers:profile_detail")
        self.assertEqual(resolve("/helpers/profile/edit/").view_name, "helpers:profile_edit")
        self.assertEqual(resolve("/helpers/profile/skills/").view_name, "helpers:skills")
        self.assertEqual(resolve("/helpers/profile/availability/").view_name, "helpers:availability")
        self.assertEqual(resolve("/helpers/profile/preview/").view_name, "helpers:profile_preview")
        self.assertEqual(resolve("/helpers/profile/incomplete/").view_name, "helpers:profile_incomplete")


class HelpersHandoffTests(TestCase):
    def setUp(self):
        self.helper = User.objects.create_user(
            username="handoff@mk.com",
            email="handoff@mk.com",
            phone_number="0760000010",
            password="StrongPass123!",
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        HelperOnboardingProfile.objects.create(
            user=self.helper,
            display_name="Nomsa M",
            location="Benoni",
            years_experience=5,
            bio="Reliable cleaner",
            selected_categories="cleaning,laundry",
            has_id_document_ready=True,
            has_criminal_check_ready=False,
            has_references=True,
            preferred_work_area="Benoni CBD",
            availability_summary="Weekdays 08:00-16:00",
            is_completed=True,
        )

    def test_helper_profile_can_be_created_from_onboarding_data(self):
        profile = create_or_update_helper_profile_from_onboarding(self.helper)
        self.assertEqual(profile.display_name, "Nomsa M")
        self.assertEqual(profile.location, "Benoni")

    def test_handoff_service_is_idempotent(self):
        create_or_update_helper_profile_from_onboarding(self.helper)
        create_or_update_helper_profile_from_onboarding(self.helper)
        self.assertEqual(HelperProfile.objects.filter(user=self.helper).count(), 1)

    def test_selected_onboarding_categories_create_helper_skills(self):
        ensure_default_service_categories()
        create_or_update_helper_profile_from_onboarding(self.helper)
        self.assertGreaterEqual(HelperSkill.objects.filter(helper__user=self.helper).count(), 2)

    def test_profile_completion_calculation_works(self):
        profile = create_or_update_helper_profile_from_onboarding(self.helper)
        percent = calculate_helper_profile_completion(profile)
        self.assertGreaterEqual(percent, 50)

    def test_trust_signals_created_from_onboarding_readiness_fields(self):
        create_or_update_helper_profile_from_onboarding(self.helper)
        self.assertEqual(HelperTrustSignal.objects.filter(helper__user=self.helper).count(), 5)

    def test_findstatic_resolves_helper_assets(self):
        css = finders.find("helpers/css/helpers.css")
        js = finders.find("helpers/js/helpers.js")
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertIn("helpers\\static\\helpers", css)
        self.assertIn("helpers\\static\\helpers", js)
