from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import resolve, reverse

from accounts.models import User
from accounts.services.redirect_service import get_role_redirect_url
from helpers.models import HelperProfile, HelperSkill, HelperTrustSignal, ServiceCategory
from worker_portal.services.dashboard_service import build_worker_dashboard_context


class WorkerPortalAccessTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.helper_complete = User.objects.create_user(
            username="worker_complete@mk.com",
            email="worker_complete@mk.com",
            phone_number="0830000001",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
            first_name="Nomsa",
        )
        self.helper_incomplete = User.objects.create_user(
            username="worker_incomplete@mk.com",
            email="worker_incomplete@mk.com",
            phone_number="0830000002",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=False,
        )
        self.employer = User.objects.create_user(
            username="worker_employer@mk.com",
            email="worker_employer@mk.com",
            phone_number="0830000003",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )

        self.routes = [
            reverse("worker_portal:dashboard"),
            reverse("worker_portal:offers"),
            reverse("worker_portal:requests"),
            reverse("worker_portal:jobs"),
            reverse("worker_portal:earnings"),
            reverse("worker_portal:messages"),
            reverse("worker_portal:verification"),
            reverse("worker_portal:reviews"),
            reverse("worker_portal:safety"),
            reverse("worker_portal:coming_soon"),
        ]

    def test_anonymous_redirected_to_login_from_worker_dashboard(self):
        response = self.client.get(reverse("worker_portal:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_employer_cannot_access_worker_portal(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("worker_portal:dashboard"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_incomplete_helper_redirects_to_onboarding_start(self):
        self.client.force_login(self.helper_incomplete)
        response = self.client.get(reverse("worker_portal:dashboard"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_complete_helper_can_access_dashboard(self):
        self.client.force_login(self.helper_complete)
        response = self.client.get(reverse("worker_portal:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_complete_helper_can_access_all_worker_portal_pages(self):
        self.client.force_login(self.helper_complete)
        for route in self.routes:
            response = self.client.get(route)
            if route == reverse("worker_portal:messages"):
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, reverse("messaging:inbox"))
            elif route == reverse("worker_portal:earnings"):
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, reverse("payments:worker_earnings"))
            elif route == reverse("worker_portal:requests"):
                self.assertRedirects(response, reverse("worker_portal:offers"), fetch_redirect_response=False)
            else:
                self.assertEqual(response.status_code, 200)


class WorkerPortalDomainIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="worker_domain@mk.com",
            email="worker_domain@mk.com",
            phone_number="0831000001",
            password="StrongPass123!",
            role=User.Role.HELPER,
            is_onboarding_complete=True,
            first_name="Nomsa",
        )

    def test_dashboard_uses_helpers_domain_data(self):
        profile = HelperProfile.objects.create(
            user=self.user,
            display_name="Nomsa D",
            location="Benoni",
            availability_summary="Weekdays 08:00-16:00",
            profile_completion_percent=81,
            trust_status=HelperProfile.TrustStatus.READY_FOR_REVIEW,
            is_active=True,
        )
        category = ServiceCategory.objects.create(name="Cleaning", slug="cleaning", is_active=True, sort_order=1)
        HelperSkill.objects.create(helper=profile, category=category, years_experience=3)
        HelperTrustSignal.objects.create(
            helper=profile,
            signal_type=HelperTrustSignal.SignalType.ID_DOCUMENT,
            status=HelperTrustSignal.SignalStatus.READY,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("worker_portal:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nomsa")
        self.assertContains(response, "81%")
        self.assertContains(response, "Work profile readiness")

    def test_dashboard_handles_missing_helper_profile_safely(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("worker_portal:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Work profile readiness")

    def test_placeholder_pages_load(self):
        self.client.force_login(self.user)
        requests_response = self.client.get(reverse("worker_portal:requests"))
        self.assertRedirects(requests_response, reverse("worker_portal:offers"), fetch_redirect_response=False)
        offers_response = self.client.get(reverse("worker_portal:offers"))
        self.assertEqual(offers_response.status_code, 200)
        for route_name in [
            "worker_portal:jobs",
            "worker_portal:verification",
            "worker_portal:reviews",
            "worker_portal:safety",
        ]:
            response = self.client.get(reverse(route_name))
            self.assertEqual(response.status_code, 200)
        earnings_response = self.client.get(reverse("worker_portal:earnings"))
        self.assertEqual(earnings_response.status_code, 302)
        self.assertEqual(earnings_response.url, reverse("payments:worker_earnings"))
        messages_response = self.client.get(reverse("worker_portal:messages"))
        self.assertEqual(messages_response.status_code, 302)
        self.assertEqual(messages_response.url, reverse("messaging:inbox"))

    def test_profile_link_points_to_helpers_profile_route(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("worker_portal:dashboard"))
        self.assertContains(response, reverse("helpers:profile_detail"))

    def test_dashboard_service_builds_context(self):
        context = build_worker_dashboard_context(self.user)
        self.assertIn("profile_completion_percent", context)
        self.assertIn("next_actions", context)


class WorkerPortalRoutingAndRedirectTests(TestCase):
    def test_routes_resolve_correctly(self):
        self.assertEqual(resolve("/worker/").view_name, "worker_portal:dashboard")
        self.assertEqual(resolve("/worker/offers/").view_name, "worker_portal:offers")
        self.assertEqual(resolve("/worker/requests/").view_name, "worker_portal:requests")
        self.assertEqual(resolve("/worker/jobs/").view_name, "worker_portal:jobs")
        self.assertEqual(resolve("/worker/earnings/").view_name, "worker_portal:earnings")
        self.assertEqual(resolve("/worker/messages/").view_name, "worker_portal:messages")
        self.assertEqual(resolve("/worker/verification/").view_name, "worker_portal:verification")
        self.assertEqual(resolve("/worker/reviews/").view_name, "worker_portal:reviews")
        self.assertEqual(resolve("/worker/safety/").view_name, "worker_portal:safety")
        self.assertEqual(resolve("/worker/coming-soon/").view_name, "worker_portal:coming_soon")

    def test_static_files_resolve(self):
        css = finders.find("worker_portal/css/worker_portal.css")
        js = finders.find("worker_portal/js/worker_portal.js")
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertIn("worker_portal\\static\\worker_portal", css)
        self.assertIn("worker_portal\\static\\worker_portal", js)

    def test_completed_helper_redirect_goes_to_worker_portal(self):
        helper = User.objects.create_user(
            username="redirect_helper@mk.com",
            email="redirect_helper@mk.com",
            phone_number="0832000001",
            password="StrongPass123!",
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.assertEqual(get_role_redirect_url(helper), reverse("worker_portal:dashboard"))

    def test_employer_redirect_to_employer_portal_remains_unaffected(self):
        employer = User.objects.create_user(
            username="redirect_employer@mk.com",
            email="redirect_employer@mk.com",
            phone_number="0832000002",
            password="StrongPass123!",
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.assertEqual(get_role_redirect_url(employer), reverse("employer_portal:dashboard"))
