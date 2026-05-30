from datetime import time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from bookings.services.booking_service import create_booking_request
from employers.models import EmployerLocation, EmployerProfile
from helpers.models import HelperProfile, ServiceCategory


class WorkerOffersPageTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.employer_user = User.objects.create_user(
            username="offers_employer@mk.com",
            email="offers_employer@mk.com",
            phone_number="0711000001",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.worker_user = User.objects.create_user(
            username="offers_worker@mk.com",
            email="offers_worker@mk.com",
            phone_number="0711000003",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            display_name="Offers Employer",
            contact_number="0829998888",
            primary_area="Benoni",
            is_active=True,
            is_profile_complete=True,
        )
        self.employer_location = EmployerLocation.objects.create(
            employer=self.employer_profile,
            label="Home",
            suburb="Benoni",
            city="Ekurhuleni",
            is_primary=True,
            is_active=True,
        )
        self.worker_profile = HelperProfile.objects.create(
            user=self.worker_user,
            display_name="Offers Worker",
            location="Benoni",
            is_active=True,
            is_profile_complete=True,
        )
        self.service_category = ServiceCategory.objects.create(name="Cleaning", slug="cleaning-offers", is_active=True)

    def test_offers_page_lists_pending_booking_without_private_contact(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            worker_profile=self.worker_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=2),
            start_time=time(10, 0),
            duration_hours=3,
            special_instructions="Use side gate",
            created_by=self.employer_user,
        )
        self.assertEqual(booking.status, Booking.Status.PENDING_WORKER_RESPONSE)

        self.client.force_login(self.worker_user)
        response = self.client.get(reverse("worker_portal:offers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Offers Employer")
        self.assertContains(response, "Accept offer")
        self.assertContains(response, "Use side gate")
        self.assertNotContains(response, "0829998888")
        self.assertNotContains(response, "0711000001")

    def test_bookings_worker_requests_redirects_to_portal_offers(self):
        create_booking_request(
            employer_profile=self.employer_profile,
            worker_profile=self.worker_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=2),
            start_time=time(10, 0),
            duration_hours=3,
            special_instructions="",
            created_by=self.employer_user,
        )
        self.client.force_login(self.worker_user)
        response = self.client.get(reverse("bookings:worker_requests"))
        self.assertRedirects(response, reverse("worker_portal:offers"), fetch_redirect_response=False)

    def test_worker_portal_requests_redirects_to_offers(self):
        self.client.force_login(self.worker_user)
        response = self.client.get(reverse("worker_portal:requests"))
        self.assertRedirects(response, reverse("worker_portal:offers"), fetch_redirect_response=False)
