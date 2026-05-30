from datetime import time, timedelta
from decimal import Decimal

from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from bookings.forms import EmployerBookingRequestForm
from bookings.models import Booking, BookingApplication, BookingEvent
from bookings.services.booking_service import create_booking_request
from employers.models import EmployerLocation, EmployerProfile
from helpers.models import HelperProfile, HelperSkill, HelperTrustSignal, ServiceCategory, WorkerVerificationDocument
from helpers.services.verification_service import review_worker_verification_document, upload_worker_verification_document


class BookingWorkflowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.employer_user = User.objects.create_user(
            username="employer_booking@mk.com",
            email="employer_booking@mk.com",
            phone_number="0710000001",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.employer_other_user = User.objects.create_user(
            username="employer_other@mk.com",
            email="employer_other@mk.com",
            phone_number="0710000002",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.worker_user = User.objects.create_user(
            username="worker_booking@mk.com",
            email="worker_booking@mk.com",
            phone_number="0710000003",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.worker_other_user = User.objects.create_user(
            username="worker_other@mk.com",
            email="worker_other@mk.com",
            phone_number="0710000004",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )

        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            display_name="Zipho Employer",
            primary_area="Benoni",
            is_active=True,
            is_profile_complete=True,
        )
        self.employer_other_profile = EmployerProfile.objects.create(
            user=self.employer_other_user,
            display_name="Other Employer",
            primary_area="Boksburg",
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
        self.employer_other_location = EmployerLocation.objects.create(
            employer=self.employer_other_profile,
            label="Office",
            suburb="Boksburg",
            city="Ekurhuleni",
            is_primary=True,
            is_active=True,
        )

        self.worker_profile = HelperProfile.objects.create(
            user=self.worker_user,
            display_name="Nomsa Worker",
            location="Benoni",
            is_active=True,
            is_profile_complete=True,
        )
        self.worker_other_profile = HelperProfile.objects.create(
            user=self.worker_other_user,
            display_name="Other Worker",
            location="Kempton Park",
            is_active=True,
            is_profile_complete=True,
        )

        self.service_category = ServiceCategory.objects.create(name="Cleaning", slug="cleaning", is_active=True)
        self.other_category = ServiceCategory.objects.create(name="Laundry", slug="laundry", is_active=True)

        HelperSkill.objects.create(helper=self.worker_profile, category=self.service_category, years_experience=2)
        HelperSkill.objects.create(helper=self.worker_other_profile, category=self.service_category, years_experience=2)

    def _booking_payload(self):
        return {
            "request_type": Booking.RequestType.DIRECT_REQUEST,
            "worker": self.worker_profile.id,
            "service_category": self.service_category.id,
            "employer_location": self.employer_location.id,
            "scheduled_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "start_time": "09:00",
            "duration_hours": 4,
            "special_instructions": "Gate code 1234",
        }

    def _create_booking(self):
        return create_booking_request(
            employer_profile=self.employer_profile,
            worker_profile=self.worker_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
        )

    def test_anonymous_user_redirected_from_employer_routes(self):
        response = self.client.get(reverse("bookings:employer_bookings"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_anonymous_user_redirected_from_worker_routes(self):
        response = self.client.get(reverse("bookings:worker_requests"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_employer_can_create_booking_request(self):
        self.client.force_login(self.employer_user)
        response = self.client.post(reverse("bookings:employer_booking_create"), data=self._booking_payload())
        self.assertEqual(response.status_code, 302)
        booking = Booking.objects.get()
        self.assertEqual(booking.status, Booking.Status.PENDING_WORKER_RESPONSE)

    def test_booking_request_creates_event(self):
        self.client.force_login(self.employer_user)
        self.client.post(reverse("bookings:employer_booking_create"), data=self._booking_payload())
        booking = Booking.objects.get()
        event = booking.events.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, BookingEvent.EventType.REQUEST_CREATED)

    def test_pricing_estimate_is_calculated(self):
        booking = self._create_booking()
        self.assertEqual(booking.worker_fee_estimate, Decimal("300.00"))
        self.assertEqual(booking.platform_fee_estimate, Decimal("45.00"))
        self.assertEqual(booking.total_estimate, Decimal("345.00"))

    def test_worker_sees_assigned_pending_request(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        response = self.client.get(reverse("worker_portal:offers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, booking.booking_reference)

    def test_employer_sees_booking_confirmed_after_worker_accept(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        self.client.post(reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference}))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.ACCEPTED)

        self.client.force_login(self.employer_user)
        list_response = self.client.get(reverse("bookings:employer_bookings"))
        self.assertContains(list_response, "Booking confirmed")
        detail_response = self.client.get(
            reverse("bookings:employer_booking_detail", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertContains(detail_response, "Booking confirmed")

    def test_worker_request_detail_shows_employer_location(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        response = self.client.get(
            reverse("bookings:worker_request_detail", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Benoni")
        self.assertContains(response, "Home")

    def test_worker_cannot_see_another_workers_request(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_other_user)
        response = self.client.get(reverse("bookings:worker_request_detail", kwargs={"booking_reference": booking.booking_reference}))
        self.assertEqual(response.status_code, 404)

    def test_worker_can_accept_assigned_booking(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        response = self.client.post(
            reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.ACCEPTED)
        self.assertTrue(booking.events.filter(event_type=BookingEvent.EventType.WORKER_ACCEPTED).exists())

    def test_worker_can_decline_assigned_booking(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        response = self.client.post(
            reverse("bookings:worker_decline_booking", kwargs={"booking_reference": booking.booking_reference}),
            data={"reason": "Already booked"},
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.DECLINED)
        self.assertEqual(booking.decline_reason, "Already booked")

    def test_employer_can_cancel_own_booking(self):
        booking = self._create_booking()
        self.client.force_login(self.employer_user)
        response = self.client.post(
            reverse("bookings:employer_cancel_booking", kwargs={"booking_reference": booking.booking_reference}),
            data={"reason": "Plans changed"},
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED_BY_EMPLOYER)

    def test_worker_can_cancel_accepted_booking(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        self.client.post(reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference}))
        response = self.client.post(
            reverse("bookings:worker_cancel_booking", kwargs={"booking_reference": booking.booking_reference}),
            data={"reason": "Emergency"},
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED_BY_WORKER)

    def test_employer_can_mark_accepted_booking_complete(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        self.client.post(reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference}))

        self.client.force_login(self.employer_user)
        response = self.client.post(
            reverse("bookings:employer_mark_completed", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.COMPLETED)
        self.assertIsNotNone(booking.completed_at)

    def test_invalid_transition_is_blocked(self):
        booking = self._create_booking()
        self.client.force_login(self.worker_user)
        self.client.post(
            reverse("bookings:worker_decline_booking", kwargs={"booking_reference": booking.booking_reference}),
            data={"reason": "Unavailable"},
        )
        response = self.client.post(
            reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.DECLINED)

    def test_wrong_role_cannot_access_employer_routes(self):
        self.client.force_login(self.worker_user)
        response = self.client.get(reverse("bookings:employer_bookings"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_wrong_role_cannot_access_worker_routes(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("bookings:worker_requests"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_booking_timeline_loads(self):
        booking = self._create_booking()
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("bookings:booking_timeline", kwargs={"booking_reference": booking.booking_reference}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booking timeline")

    def test_booking_reference_is_unique(self):
        first = self._create_booking()
        second = create_booking_request(
            employer_profile=self.employer_profile,
            worker_profile=self.worker_other_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=2),
            start_time=time(10, 0),
            duration_hours=3,
            special_instructions="Bring supplies",
            created_by=self.employer_user,
        )
        self.assertNotEqual(first.booking_reference, second.booking_reference)

    def test_form_prevents_past_scheduled_date(self):
        form = EmployerBookingRequestForm(
            data={
                **self._booking_payload(),
                "scheduled_date": (timezone.localdate() - timedelta(days=1)).isoformat(),
            },
            user=self.employer_user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("scheduled_date", form.errors)

    def test_form_prevents_invalid_duration(self):
        form = EmployerBookingRequestForm(
            data={
                **self._booking_payload(),
                "duration_hours": 0,
            },
            user=self.employer_user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("duration_hours", form.errors)

    def test_static_files_resolve_to_bookings_paths(self):
        css = finders.find("bookings/css/bookings.css")
        js = finders.find("bookings/js/bookings.js")
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertIn("bookings\\static\\bookings", css)
        self.assertIn("bookings\\static\\bookings", js)

    def test_portal_links_point_to_bookings_routes(self):
        self.client.force_login(self.employer_user)
        employer_find_help = self.client.get(reverse("employer_portal:find_help"))
        self.assertContains(employer_find_help, reverse("bookings:employer_booking_create"))
        self.assertContains(employer_find_help, reverse("bookings:employer_marketplace_jobs"))

        employer_bookings = self.client.get(reverse("employer_portal:bookings"))
        self.assertRedirects(employer_bookings, reverse("bookings:employer_bookings"), fetch_redirect_response=False)

        self.client.force_login(self.worker_user)
        worker_requests = self.client.get(reverse("worker_portal:requests"))
        self.assertRedirects(worker_requests, reverse("worker_portal:offers"), fetch_redirect_response=False)
        offers_page = self.client.get(reverse("worker_portal:offers"))
        self.assertContains(offers_page, reverse("bookings:worker_available_jobs"))

        worker_jobs = self.client.get(reverse("worker_portal:jobs"))
        self.assertContains(worker_jobs, reverse("bookings:worker_jobs"))
        self.assertContains(worker_jobs, reverse("bookings:worker_my_applications"))

    def test_employer_can_create_marketplace_job_without_worker(self):
        self.client.force_login(self.employer_user)
        payload = self._booking_payload()
        payload["request_type"] = Booking.RequestType.OPEN_MARKETPLACE
        payload["worker"] = ""
        response = self.client.post(reverse("bookings:employer_booking_create"), data=payload)
        self.assertEqual(response.status_code, 302)
        booking = Booking.objects.latest("id")
        self.assertEqual(booking.request_type, Booking.RequestType.OPEN_MARKETPLACE)
        self.assertEqual(booking.status, Booking.Status.OPEN_FOR_APPLICATIONS)
        self.assertIsNone(booking.worker)

    def test_employer_create_page_disables_worker_step_for_marketplace(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("bookings:employer_booking_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-booking-worker-step")

    def test_worker_marketplace_lists_job_location(self):
        create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        response = self.client.get(reverse("bookings:worker_available_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Benoni")
        self.assertContains(response, "Home")

    def test_worker_apply_page_shows_employer_profile_not_private_contact(self):
        self.employer_profile.contact_number = "0829998888"
        self.employer_profile.save()
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        response = self.client.get(
            reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Zipho Employer")
        self.assertContains(response, "Benoni")
        self.assertContains(response, "Profile complete")
        self.assertContains(response, "Gate code 1234")
        self.assertNotContains(response, "0829998888")
        self.assertNotContains(response, "0710000001")

    def test_employer_applications_page_shows_safe_trust_badges_not_private_data(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        self.client.post(
            reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}),
            data={"message": "I am available for this job.", "proposed_fee": "300.00"},
        )
        id_document = upload_worker_verification_document(
            user=self.worker_user,
            document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
            uploaded_file=SimpleUploadedFile("id.pdf", b"%PDF-1.4 test\n%%EOF", content_type="application/pdf"),
        )
        staff = User.objects.create_user(
            username="booking_staff@mk.com",
            email="booking_staff@mk.com",
            phone_number="0710000099",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
            is_staff=True,
        )
        review_worker_verification_document(
            document=id_document,
            reviewer=staff,
            status=WorkerVerificationDocument.Status.APPROVED,
        )
        HelperTrustSignal.objects.filter(
            helper=self.worker_profile,
            signal_type=HelperTrustSignal.SignalType.CRIMINAL_RECORD_CHECK,
        ).update(status=HelperTrustSignal.SignalStatus.PENDING_REVIEW)

        self.client.force_login(self.employer_user)
        response = self.client.get(
            reverse("bookings:employer_booking_applications", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ID verified")
        self.assertContains(response, "Nomsa Worker")
        self.assertNotContains(response, "0710000003")
        self.assertNotContains(response, "/media/helpers/verification/")

    def test_helper_can_apply_to_open_job(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        response = self.client.post(
            reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}),
            data={"message": "Available", "proposed_fee": "250.00"},
        )
        self.assertEqual(response.status_code, 302)
        application = BookingApplication.objects.get(booking=booking, worker=self.worker_profile)
        self.assertEqual(application.status, BookingApplication.Status.PENDING)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.APPLICATIONS_RECEIVED)

    def test_duplicate_application_is_blocked(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        apply_url = reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference})
        self.client.post(apply_url, data={"message": "First"})
        self.client.post(apply_url, data={"message": "Second"})
        self.assertEqual(BookingApplication.objects.filter(booking=booking, worker=self.worker_profile).count(), 1)

    def test_employer_selects_applicant_then_worker_confirms(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        self.client.post(reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}), data={"message": "I can do this"})
        application = BookingApplication.objects.get(booking=booking, worker=self.worker_profile)

        self.client.force_login(self.employer_user)
        self.client.post(reverse("bookings:employer_select_application", kwargs={"application_id": application.id}))
        booking.refresh_from_db()
        self.assertEqual(booking.worker_id, self.worker_profile.id)
        self.assertEqual(booking.status, Booking.Status.PENDING_WORKER_RESPONSE)

        self.client.force_login(self.worker_user)
        self.client.post(reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference}))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.ACCEPTED)

    def test_selected_application_shows_review_offer_link(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Pick me at gate",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        self.client.post(
            reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}),
            data={"message": "Pick me"},
        )
        application = BookingApplication.objects.get(booking=booking, worker=self.worker_profile)
        self.client.force_login(self.employer_user)
        self.client.post(reverse("bookings:employer_select_application", kwargs={"application_id": application.id}))

        self.client.force_login(self.worker_user)
        response = self.client.get(reverse("bookings:worker_my_applications"))
        self.assertContains(response, "Review offer")
        self.assertContains(response, reverse("bookings:worker_request_detail", kwargs={"booking_reference": booking.booking_reference}))

    def test_worker_cannot_access_other_application(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        self.client.post(reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}), data={"message": "A"})
        application = BookingApplication.objects.get(booking=booking, worker=self.worker_profile)
        self.client.force_login(self.worker_other_user)
        response = self.client.post(reverse("bookings:worker_withdraw_application", kwargs={"application_id": application.id}))
        self.assertEqual(response.status_code, 404)

    def test_non_selected_helper_cannot_accept_selected_marketplace_booking(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        self.client.post(
            reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}),
            data={"message": "Primary applicant"},
        )
        self.client.force_login(self.worker_other_user)
        self.client.post(
            reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}),
            data={"message": "Other applicant"},
        )

        selected_application = BookingApplication.objects.get(booking=booking, worker=self.worker_profile)
        self.client.force_login(self.employer_user)
        self.client.post(reverse("bookings:employer_select_application", kwargs={"application_id": selected_application.id}))

        booking.refresh_from_db()
        self.assertEqual(booking.worker_id, self.worker_profile.id)
        self.assertEqual(booking.status, Booking.Status.PENDING_WORKER_RESPONSE)

        non_selected_application = BookingApplication.objects.get(booking=booking, worker=self.worker_other_profile)
        self.assertEqual(non_selected_application.status, BookingApplication.Status.DECLINED)

        self.client.force_login(self.worker_other_user)
        response = self.client.post(
            reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference})
        )
        self.assertEqual(response.status_code, 404)

    def test_selected_helper_can_decline_after_employer_selection(self):
        booking = create_booking_request(
            employer_profile=self.employer_profile,
            service_category=self.service_category,
            employer_location=self.employer_location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=4,
            special_instructions="Gate code 1234",
            created_by=self.employer_user,
            request_type=Booking.RequestType.OPEN_MARKETPLACE,
        )
        self.client.force_login(self.worker_user)
        self.client.post(
            reverse("bookings:worker_apply_to_job", kwargs={"booking_reference": booking.booking_reference}),
            data={"message": "I can do this"},
        )
        selected_application = BookingApplication.objects.get(booking=booking, worker=self.worker_profile)

        self.client.force_login(self.employer_user)
        self.client.post(reverse("bookings:employer_select_application", kwargs={"application_id": selected_application.id}))

        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.PENDING_WORKER_RESPONSE)

        self.client.force_login(self.worker_user)
        response = self.client.post(
            reverse("bookings:worker_decline_booking", kwargs={"booking_reference": booking.booking_reference}),
            data={"reason": "No longer available"},
        )
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.DECLINED)
