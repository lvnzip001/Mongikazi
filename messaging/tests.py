from datetime import time, timedelta

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from bookings.services.booking_service import create_booking_request
from employers.models import EmployerLocation, EmployerProfile
from helpers.models import HelperProfile, HelperSkill, ServiceCategory
from messaging.models import Message, MessageThread


class MessagingFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.employer_user = User.objects.create_user(
            username="msg_employer@mk.com",
            email="msg_employer@mk.com",
            phone_number="0740000001",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.employer_other_user = User.objects.create_user(
            username="msg_employer_other@mk.com",
            email="msg_employer_other@mk.com",
            phone_number="0740000002",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.helper_user = User.objects.create_user(
            username="msg_helper@mk.com",
            email="msg_helper@mk.com",
            phone_number="0740000003",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.helper_other_user = User.objects.create_user(
            username="msg_helper_other@mk.com",
            email="msg_helper_other@mk.com",
            phone_number="0740000004",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )

        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            display_name="Employer A",
            primary_area="Benoni",
            is_active=True,
            is_profile_complete=True,
        )
        self.employer_other_profile = EmployerProfile.objects.create(
            user=self.employer_other_user,
            display_name="Employer B",
            primary_area="Boksburg",
            is_active=True,
            is_profile_complete=True,
        )
        self.location = EmployerLocation.objects.create(
            employer=self.employer_profile,
            label="Home",
            suburb="Benoni",
            city="Ekurhuleni",
            is_primary=True,
            is_active=True,
        )

        self.helper_profile = HelperProfile.objects.create(
            user=self.helper_user,
            display_name="Helper A",
            location="Benoni",
            is_active=True,
            is_profile_complete=True,
        )
        self.helper_other_profile = HelperProfile.objects.create(
            user=self.helper_other_user,
            display_name="Helper B",
            location="Germiston",
            is_active=True,
            is_profile_complete=True,
        )

        self.category = ServiceCategory.objects.create(name="Cleaning", slug="cleaning-msg", is_active=True)
        HelperSkill.objects.create(helper=self.helper_profile, category=self.category, years_experience=2)

        self.booking = create_booking_request(
            employer_profile=self.employer_profile,
            worker_profile=self.helper_profile,
            request_type=Booking.RequestType.DIRECT_REQUEST,
            service_category=self.category,
            employer_location=self.location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=3,
            special_instructions="Gate code",
            created_by=self.employer_user,
        )

    def test_anonymous_user_redirected_from_inbox(self):
        response = self.client.get(reverse("messaging:inbox"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_employer_can_open_booking_thread(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("messaging:open_booking_thread", kwargs={"booking_reference": self.booking.booking_reference}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MessageThread.objects.filter(booking=self.booking).exists())

    def test_helper_opens_same_existing_thread(self):
        self.client.force_login(self.employer_user)
        self.client.get(reverse("messaging:open_booking_thread", kwargs={"booking_reference": self.booking.booking_reference}))
        first = MessageThread.objects.get(booking=self.booking)

        self.client.force_login(self.helper_user)
        self.client.get(reverse("messaging:open_booking_thread", kwargs={"booking_reference": self.booking.booking_reference}))
        second = MessageThread.objects.get(booking=self.booking)
        self.assertEqual(first.id, second.id)

    def test_non_participant_cannot_open_thread(self):
        self.client.force_login(self.helper_other_user)
        response = self.client.get(reverse("messaging:open_booking_thread", kwargs={"booking_reference": self.booking.booking_reference}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MessageThread.objects.filter(booking=self.booking).exists())

    def test_participant_can_send_message(self):
        thread = MessageThread.objects.create(
            booking=self.booking,
            employer_user=self.employer_user,
            helper_user=self.helper_user,
        )
        self.client.force_login(self.employer_user)
        response = self.client.post(reverse("messaging:send_thread_message", kwargs={"thread_id": thread.id}), data={"body": "Hello"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Message.objects.filter(thread=thread, body="Hello").exists())

    def test_non_participant_cannot_view_thread(self):
        thread = MessageThread.objects.create(
            booking=self.booking,
            employer_user=self.employer_user,
            helper_user=self.helper_user,
        )
        self.client.force_login(self.employer_other_user)
        response = self.client.get(reverse("messaging:thread_detail", kwargs={"thread_id": thread.id}))
        self.assertEqual(response.status_code, 404)

    def test_mark_read_updates_read_timestamp_for_recipient(self):
        thread = MessageThread.objects.create(
            booking=self.booking,
            employer_user=self.employer_user,
            helper_user=self.helper_user,
        )
        Message.objects.create(thread=thread, sender=self.employer_user, body="Hi helper")
        self.client.force_login(self.helper_user)
        self.client.get(reverse("messaging:thread_detail", kwargs={"thread_id": thread.id}))
        msg = Message.objects.get(thread=thread)
        self.assertIsNotNone(msg.read_by_helper_at)

    def test_open_thread_requires_assigned_worker(self):
        open_booking = create_booking_request(
            employer_profile=self.employer_profile,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
            service_category=self.category,
            employer_location=self.location,
            scheduled_date=timezone.localdate() + timedelta(days=2),
            start_time=time(11, 0),
            duration_hours=2,
            special_instructions="Open role",
            created_by=self.employer_user,
        )
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("messaging:open_booking_thread", kwargs={"booking_reference": open_booking.booking_reference}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MessageThread.objects.filter(booking=open_booking).exists())

    def test_messaging_static_assets_resolve(self):
        css = finders.find("messaging/css/messaging.css")
        js = finders.find("messaging/js/messaging.js")
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertIn("messaging\\static\\messaging", css)
        self.assertIn("messaging\\static\\messaging", js)

