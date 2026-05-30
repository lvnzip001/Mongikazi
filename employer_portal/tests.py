from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import resolve, reverse

from accounts.models import User
from accounts.services.redirect_service import get_role_redirect_url
from employer_portal.services.dashboard_service import build_employer_dashboard_context
from employers.models import EmployerLocation, EmployerProfile, EmployerServicePreference
from helpers.models import HelperProfile, ServiceCategory


class EmployerPortalAccessTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.employer_complete = User.objects.create_user(
            username="portal_emp_complete@mk.com",
            email="portal_emp_complete@mk.com",
            phone_number="0810000001",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.employer_incomplete = User.objects.create_user(
            username="portal_emp_incomplete@mk.com",
            email="portal_emp_incomplete@mk.com",
            phone_number="0810000002",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=False,
        )
        self.helper = User.objects.create_user(
            username="portal_helper@mk.com",
            email="portal_helper@mk.com",
            phone_number="0810000003",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )

        self.portal_routes = [
            reverse("employer_portal:dashboard"),
            reverse("employer_portal:find_help"),
            reverse("employer_portal:bookings"),
            reverse("employer_portal:favourites"),
            reverse("employer_portal:payments"),
            reverse("employer_portal:messages"),
            reverse("employer_portal:support"),
            reverse("employer_portal:coming_soon"),
        ]

    def test_anonymous_user_redirected_to_login_from_dashboard(self):
        response = self.client.get(reverse("employer_portal:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_helper_user_cannot_access_employer_portal(self):
        self.client.force_login(self.helper)
        response = self.client.get(reverse("employer_portal:dashboard"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_incomplete_employer_redirects_to_onboarding_start(self):
        self.client.force_login(self.employer_incomplete)
        response = self.client.get(reverse("employer_portal:dashboard"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_complete_employer_can_access_dashboard(self):
        self.client.force_login(self.employer_complete)
        response = self.client.get(reverse("employer_portal:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_complete_employer_can_access_all_portal_pages(self):
        self.client.force_login(self.employer_complete)
        for route in self.portal_routes:
            response = self.client.get(route)
            if route == reverse("employer_portal:messages"):
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, reverse("messaging:inbox"))
            elif route == reverse("employer_portal:payments"):
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, reverse("payments:employer_invoices"))
            elif route == reverse("employer_portal:bookings"):
                self.assertRedirects(response, reverse("bookings:employer_bookings"), fetch_redirect_response=False)
            else:
                self.assertEqual(response.status_code, 200)

    def test_account_completed_employer_redirect_goes_to_employer_portal_dashboard(self):
        self.assertEqual(get_role_redirect_url(self.employer_complete), reverse("employer_portal:dashboard"))


class EmployerPortalDomainIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="portal_domain@mk.com",
            email="portal_domain@mk.com",
            phone_number="0811000001",
            password="StrongPass123!",
            first_name="Zipho",
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )

    def test_dashboard_uses_employers_domain_data(self):
        profile = EmployerProfile.objects.create(
            user=self.user,
            display_name="Zipho Household",
            primary_area="Benoni",
            preferred_contact_method=EmployerProfile.ContactMethod.APP,
            contact_number="0811000001",
            profile_completion_percent=78,
            trust_status=EmployerProfile.TrustStatus.READY_FOR_BOOKING,
        )
        EmployerLocation.objects.create(
            employer=profile,
            label="Home",
            address_line_1="123 Street",
            suburb="Benoni",
            city="Ekurhuleni",
            province="Gauteng",
            is_primary=True,
            is_active=True,
        )
        EmployerServicePreference.objects.create(
            employer=profile,
            service_type=EmployerServicePreference.ServiceType.ONCE_OFF_CLEANING,
            service_frequency=EmployerServicePreference.ServiceFrequency.WEEKLY,
            estimated_duration_hours=4,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("employer_portal:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Zipho")
        self.assertContains(response, "Benoni")
        self.assertContains(response, "Once-off cleaning")

    def test_dashboard_handles_missing_employer_profile_safely(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("employer_portal:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booking readiness")

    def test_find_help_page_loads_with_category_placeholder_data(self):
        ServiceCategory.objects.create(name="Cleaning", slug="cleaning", is_active=True, sort_order=1)
        helper_user = User.objects.create_user(
            username="helperteaser@mk.com",
            email="helperteaser@mk.com",
            phone_number="0811000002",
            password="StrongPass123!",
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        HelperProfile.objects.create(user=helper_user, display_name="Nomsa", location="Benoni", is_active=True)

        self.client.force_login(self.user)
        response = self.client.get(reverse("employer_portal:find_help"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cleaning")

    def test_profile_link_points_to_employers_profile_route(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("employer_portal:dashboard"))
        self.assertContains(response, reverse("employers:profile_detail"))

    def test_dashboard_service_can_build_context_without_domain_records(self):
        context = build_employer_dashboard_context(self.user)
        self.assertIn("profile_completion_percent", context)
        self.assertIn("next_actions", context)


class EmployerPortalRoutingAndStaticTests(TestCase):
    def test_routes_resolve_correctly(self):
        self.assertEqual(resolve("/employer/").view_name, "employer_portal:dashboard")
        self.assertEqual(resolve("/employer/find-help/").view_name, "employer_portal:find_help")
        self.assertEqual(resolve("/employer/bookings/").view_name, "employer_portal:bookings")
        self.assertEqual(resolve("/employer/favourites/").view_name, "employer_portal:favourites")
        self.assertEqual(resolve("/employer/payments/").view_name, "employer_portal:payments")
        self.assertEqual(resolve("/employer/messages/").view_name, "employer_portal:messages")
        self.assertEqual(resolve("/employer/support/").view_name, "employer_portal:support")
        self.assertEqual(resolve("/employer/coming-soon/").view_name, "employer_portal:coming_soon")

    def test_findstatic_resolves_employer_portal_assets(self):
        css = finders.find("employer_portal/css/employer_portal.css")
        js = finders.find("employer_portal/js/employer_portal.js")
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertIn("employer_portal\\static\\employer_portal", css)
        self.assertIn("employer_portal\\static\\employer_portal", js)
