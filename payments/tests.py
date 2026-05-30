from datetime import time, timedelta

from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from bookings.services.booking_service import create_booking_request
from bookings.services.booking_workflow_service import accept_booking, mark_booking_completed
from employers.models import EmployerLocation, EmployerProfile
from helpers.models import HelperProfile, HelperSkill, ServiceCategory
from payments.models import Invoice, Payment, PaymentProof, PayoutAuditLog


class PaymentsFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.employer_user = User.objects.create_user(
            username="pay_employer@mk.com",
            email="pay_employer@mk.com",
            phone_number="0750000001",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.employer_other_user = User.objects.create_user(
            username="pay_employer_other@mk.com",
            email="pay_employer_other@mk.com",
            phone_number="0750000002",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.helper_user = User.objects.create_user(
            username="pay_helper@mk.com",
            email="pay_helper@mk.com",
            phone_number="0750000003",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.operations_user = User.objects.create_user(
            username="pay_ops@mk.com",
            email="pay_ops@mk.com",
            phone_number="0750000004",
            password=self.password,
            role=User.Role.OPERATIONS,
            is_onboarding_complete=True,
        )

        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            display_name="Employer A",
            primary_area="Benoni",
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

        self.category = ServiceCategory.objects.create(name="Cleaning", slug="cleaning-pay", is_active=True)
        HelperSkill.objects.create(helper=self.helper_profile, category=self.category, years_experience=2)

        self.booking = create_booking_request(
            employer_profile=self.employer_profile,
            worker_profile=self.helper_profile,
            service_category=self.category,
            employer_location=self.location,
            scheduled_date=timezone.localdate() + timedelta(days=1),
            start_time=time(9, 0),
            duration_hours=3,
            special_instructions="Gate code",
            created_by=self.employer_user,
        )
        accept_booking(self.booking, self.helper_user)
        self.booking.refresh_from_db()

    def _complete_booking(self):
        mark_booking_completed(self.booking, self.employer_user)
        self.booking.refresh_from_db()
        return Invoice.objects.get(booking=self.booking)

    def test_booking_completion_issues_invoice(self):
        invoice = self._complete_booking()
        self.assertEqual(invoice.status, Invoice.Status.ISSUED)
        self.assertEqual(invoice.employer_user_id, self.employer_user.id)
        self.assertEqual(invoice.helper_user_id, self.helper_user.id)

    def test_anonymous_redirected_from_employer_invoices(self):
        response = self.client.get(reverse("payments:employer_invoices"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_employer_can_view_own_invoices(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("payments:employer_invoices"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)
        self.assertContains(response, 'aria-label="Employer portal navigation"')
        self.assertContains(response, "data-portal-more-open")
        self.assertContains(response, reverse("employer_portal:payments"))

    def test_other_employer_cannot_view_invoice_detail(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_other_user)
        response = self.client.get(reverse("payments:employer_invoice_detail", kwargs={"invoice_id": invoice.id}))
        self.assertEqual(response.status_code, 404)

    def test_employer_can_submit_payment_proof(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_user)
        response = self.client.post(
            reverse("payments:employer_submit_payment_proof", kwargs={"invoice_id": invoice.id}),
            data={
                "method": Payment.Method.EFT,
                "amount": "258.75",
                "payer_reference": "ABC123",
                "note": "Payment sent",
                "document_url": "https://example.com/proof/abc123",
            },
        )
        self.assertEqual(response.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.PROOF_SUBMITTED)
        payment = Payment.objects.get(invoice=invoice)
        self.assertEqual(payment.status, Payment.Status.SUBMITTED)
        proof = PaymentProof.objects.get(payment=payment)
        self.assertEqual(proof.document_url, "https://example.com/proof/abc123")

    def test_helper_can_view_earnings_page(self):
        invoice = self._complete_booking()
        self.client.force_login(self.helper_user)
        response = self.client.get(reverse("payments:worker_earnings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.invoice_number)
        self.assertContains(response, "My Work")
        self.assertContains(response, reverse("worker_portal:earnings"))
        self.assertContains(response, "data-worker-more-open")
        self.assertContains(response, 'aria-label="Worker portal navigation"')
        self.assertContains(response, 'aria-label="Mobile navigation"')

    def test_employer_redirects_from_worker_earnings(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("payments:worker_earnings"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("onboarding:start"))

    def test_findstatic_resolves_payments_assets(self):
        css = finders.find("payments/css/payments.css")
        js = finders.find("payments/js/payments.js")
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertIn("payments\\static\\payments", css)
        self.assertIn("payments\\static\\payments", js)

    def test_operations_can_verify_submitted_payment_and_mark_invoice_paid(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_user)
        self.client.post(
            reverse("payments:employer_submit_payment_proof", kwargs={"invoice_id": invoice.id}),
            data={
                "method": Payment.Method.EFT,
                "amount": str(invoice.total_amount),
                "payer_reference": "REF1",
                "note": "Submitted",
                "document_url": "https://example.com/proof/verify",
            },
        )
        payment = Payment.objects.get(invoice=invoice)
        self.assertEqual(payment.status, Payment.Status.SUBMITTED)

        self.client.force_login(self.operations_user)
        response = self.client.post(reverse("payments:operations_verify_payment", kwargs={"payment_id": payment.id}))
        self.assertEqual(response.status_code, 302)

        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.VERIFIED)
        self.assertEqual(invoice.status, Invoice.Status.PAID)
        self.assertIsNotNone(invoice.paid_at)
        self.assertEqual(invoice.payout_status, Invoice.PayoutStatus.READY_FOR_PAYOUT)

    def test_operations_can_reject_submitted_payment(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_user)
        self.client.post(
            reverse("payments:employer_submit_payment_proof", kwargs={"invoice_id": invoice.id}),
            data={
                "method": Payment.Method.EFT,
                "amount": "100.00",
                "payer_reference": "REF2",
                "note": "Submitted",
                "document_url": "https://example.com/proof/reject",
            },
        )
        payment = Payment.objects.get(invoice=invoice)
        self.client.force_login(self.operations_user)
        response = self.client.post(reverse("payments:operations_reject_payment", kwargs={"payment_id": payment.id}))
        self.assertEqual(response.status_code, 302)

        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.REJECTED)
        self.assertEqual(invoice.status, Invoice.Status.ISSUED)

    def test_non_operations_cannot_access_operations_review(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("payments:operations_payments_review"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("onboarding:start"))

    def test_operations_review_includes_ops_navigation(self):
        self.client.force_login(self.operations_user)
        response = self.client.get(reverse("payments:operations_payments_review"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-label="Payments operations"')
        self.assertContains(response, "Payment review")
        self.assertContains(response, reverse("payments:operations_payout_history"))
        self.assertContains(response, "mk-subnav")

    def test_operations_can_mark_paid_out_after_invoice_paid(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_user)
        self.client.post(
            reverse("payments:employer_submit_payment_proof", kwargs={"invoice_id": invoice.id}),
            data={
                "method": Payment.Method.EFT,
                "amount": str(invoice.total_amount),
                "payer_reference": "REF3",
                "note": "Submitted",
                "document_url": "https://example.com/proof/payout",
            },
        )
        payment = Payment.objects.get(invoice=invoice)
        self.client.force_login(self.operations_user)
        self.client.post(reverse("payments:operations_verify_payment", kwargs={"payment_id": payment.id}))
        invoice.refresh_from_db()
        self.assertEqual(invoice.payout_status, Invoice.PayoutStatus.READY_FOR_PAYOUT)

        response = self.client.post(
            reverse("payments:operations_mark_paid_out", kwargs={"invoice_id": invoice.id}),
            data={"payout_reference": "BATCH-001", "note": "Paid in ops batch"},
        )
        self.assertEqual(response.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.payout_status, Invoice.PayoutStatus.PAID_OUT)
        self.assertIsNotNone(invoice.paid_out_at)
        self.assertEqual(invoice.paid_out_by_id, self.operations_user.id)
        self.assertEqual(invoice.payout_reference, "BATCH-001")
        audit = PayoutAuditLog.objects.get(invoice=invoice)
        self.assertEqual(audit.performed_by_id, self.operations_user.id)
        self.assertEqual(audit.payout_reference, "BATCH-001")

    def test_non_operations_cannot_mark_paid_out(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_user)
        response = self.client.post(reverse("payments:operations_mark_paid_out", kwargs={"invoice_id": invoice.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("onboarding:start"))

    def test_operations_can_view_payout_history_and_export_csv(self):
        invoice = self._complete_booking()
        self.client.force_login(self.employer_user)
        self.client.post(
            reverse("payments:employer_submit_payment_proof", kwargs={"invoice_id": invoice.id}),
            data={
                "method": Payment.Method.EFT,
                "amount": str(invoice.total_amount),
                "payer_reference": "REF4",
                "note": "Submitted",
                "document_url": "https://example.com/proof/history",
            },
        )
        payment = Payment.objects.get(invoice=invoice)
        self.client.force_login(self.operations_user)
        self.client.post(reverse("payments:operations_verify_payment", kwargs={"payment_id": payment.id}))
        self.client.post(
            reverse("payments:operations_mark_paid_out", kwargs={"invoice_id": invoice.id}),
            data={"payout_reference": "BATCH-CSV", "note": "CSV payout"},
        )

        history_response = self.client.get(reverse("payments:operations_payout_history"))
        self.assertEqual(history_response.status_code, 200)
        self.assertContains(history_response, invoice.invoice_number)
        self.assertContains(history_response, "BATCH-CSV")

        export_response = self.client.get(reverse("payments:operations_payout_history_csv"))
        self.assertEqual(export_response.status_code, 200)
        self.assertIn("text/csv", export_response["Content-Type"])
        self.assertIn("BATCH-CSV", export_response.content.decode())

    def test_non_operations_cannot_access_payout_history_export(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("payments:operations_payout_history_csv"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("onboarding:start"))




