from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ValidationError
from django.test import TestCase

from accounts.models import User
from helpers.models import HelperProfile, HelperTrustSignal, WorkerVerificationDocument
from helpers.selectors.verification_selectors import build_employer_safe_worker_card, build_worker_verification_summary
from helpers.services.onboarding_handoff_service import sync_helper_trust_signals_from_onboarding
from helpers.services.verification_service import review_worker_verification_document, upload_worker_verification_document
from onboarding.models import HelperOnboardingProfile


MINIMAL_PDF = b"%PDF-1.4 minimal test document\n%%EOF"


class WorkerVerificationTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.helper = User.objects.create_user(
            username="verify_helper@mk.com",
            email="verify_helper@mk.com",
            phone_number="0820000101",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.other_helper = User.objects.create_user(
            username="verify_other@mk.com",
            email="verify_other@mk.com",
            phone_number="0820000102",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.staff = User.objects.create_user(
            username="verify_staff@mk.com",
            email="verify_staff@mk.com",
            phone_number="0820000103",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
            is_staff=True,
        )
        self.employer = User.objects.create_user(
            username="verify_employer@mk.com",
            email="verify_employer@mk.com",
            phone_number="0820000104",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.helper_profile = HelperProfile.objects.create(
            user=self.helper,
            display_name="Nomsa Verified",
            location="Benoni",
            bio="Reliable cleaner",
            years_experience=3,
            is_profile_complete=True,
        )
        HelperProfile.objects.create(user=self.other_helper, display_name="Other Helper", location="Pretoria")
        HelperOnboardingProfile.objects.create(
            user=self.helper,
            display_name="Nomsa Verified",
            location="Benoni",
            has_id_document_ready=True,
            has_criminal_check_ready=False,
            is_completed=True,
        )

    def _pdf_upload(self, name="id.pdf"):
        return SimpleUploadedFile(name, MINIMAL_PDF, content_type="application/pdf")

    def test_upload_sets_pending_review_trust_signal(self):
        upload_worker_verification_document(
            user=self.helper,
            document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
            uploaded_file=self._pdf_upload(),
        )
        signal = HelperTrustSignal.objects.get(
            helper=self.helper_profile,
            signal_type=HelperTrustSignal.SignalType.ID_DOCUMENT,
        )
        self.assertEqual(signal.status, HelperTrustSignal.SignalStatus.PENDING_REVIEW)
        summary = build_worker_verification_summary(self.helper_profile)
        self.assertEqual(summary["key"], "pending")

    def test_staff_review_approves_document_and_updates_summary(self):
        document = upload_worker_verification_document(
            user=self.helper,
            document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
            uploaded_file=self._pdf_upload("id.pdf"),
        )
        upload_worker_verification_document(
            user=self.helper,
            document_type=WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK,
            uploaded_file=self._pdf_upload("criminal.pdf"),
        )
        criminal = WorkerVerificationDocument.objects.get(
            helper=self.helper_profile,
            document_type=WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK,
            is_current=True,
        )
        review_worker_verification_document(
            document=document,
            reviewer=self.staff,
            status=WorkerVerificationDocument.Status.APPROVED,
        )
        review_worker_verification_document(
            document=criminal,
            reviewer=self.staff,
            status=WorkerVerificationDocument.Status.APPROVED,
        )
        summary = build_worker_verification_summary(self.helper_profile)
        self.assertEqual(summary["key"], "verified")
        self.helper_profile.refresh_from_db()
        self.assertTrue(self.helper_profile.is_verified)

    def test_onboarding_handoff_does_not_overwrite_approved_document_signal(self):
        document = upload_worker_verification_document(
            user=self.helper,
            document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
            uploaded_file=self._pdf_upload(),
        )
        review_worker_verification_document(
            document=document,
            reviewer=self.staff,
            status=WorkerVerificationDocument.Status.APPROVED,
        )
        sync_helper_trust_signals_from_onboarding(self.helper)
        signal = HelperTrustSignal.objects.get(
            helper=self.helper_profile,
            signal_type=HelperTrustSignal.SignalType.ID_DOCUMENT,
        )
        self.assertEqual(signal.status, HelperTrustSignal.SignalStatus.APPROVED)

    def test_employer_safe_card_excludes_phone_and_file_urls(self):
        upload_worker_verification_document(
            user=self.helper,
            document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
            uploaded_file=self._pdf_upload(),
        )
        card = build_employer_safe_worker_card(self.helper_profile)
        card_text = str(card)
        self.assertIn("Nomsa Verified", card["display_name"])
        self.assertNotIn("0820000101", card_text)
        self.assertNotIn("/media/helpers/verification/", card_text)
        self.assertTrue(any("ID pending review" in badge["label"] for badge in card["badges"]))

    def test_non_helper_cannot_upload_verification_document(self):
        with self.assertRaises(ValidationError):
            upload_worker_verification_document(
                user=self.employer,
                document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
                uploaded_file=self._pdf_upload(),
            )

    def test_profile_detail_reflects_admin_approved_documents(self):
        from django.urls import reverse

        id_document = upload_worker_verification_document(
            user=self.helper,
            document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
            uploaded_file=self._pdf_upload("id.pdf"),
        )
        criminal = upload_worker_verification_document(
            user=self.helper,
            document_type=WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK,
            uploaded_file=self._pdf_upload("criminal.pdf"),
        )
        review_worker_verification_document(
            document=id_document,
            reviewer=self.staff,
            status=WorkerVerificationDocument.Status.APPROVED,
        )
        review_worker_verification_document(
            document=criminal,
            reviewer=self.staff,
            status=WorkerVerificationDocument.Status.APPROVED,
        )

        self.client.force_login(self.helper)
        response = self.client.get(reverse("helpers:profile_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Verified")
        self.assertContains(response, "Approved")
        self.assertNotContains(response, "Pending review")
