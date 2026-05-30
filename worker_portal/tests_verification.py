from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from helpers.models import HelperProfile, HelperTrustSignal, WorkerVerificationDocument

MINIMAL_PDF = b"%PDF-1.4 minimal test document\n%%EOF"


class WorkerPortalVerificationTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.helper = User.objects.create_user(
            username="portal_verify@mk.com",
            email="portal_verify@mk.com",
            phone_number="0830000201",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.employer = User.objects.create_user(
            username="portal_employer@mk.com",
            email="portal_employer@mk.com",
            phone_number="0830000202",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        HelperProfile.objects.create(user=self.helper, display_name="Portal Helper", location="Benoni")

    def test_helper_can_access_verification_page(self):
        self.client.force_login(self.helper)
        response = self.client.get(reverse("worker_portal:verification"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Document centre")
        self.assertContains(response, "ID document")
        self.assertContains(response, "Criminal record check")

    def test_helper_can_upload_id_document(self):
        self.client.force_login(self.helper)
        response = self.client.post(
            reverse("worker_portal:verification_upload"),
            data={
                "document_type": WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
                "file": SimpleUploadedFile("id.pdf", MINIMAL_PDF, content_type="application/pdf"),
            },
        )
        self.assertRedirects(response, reverse("worker_portal:verification"))
        self.assertTrue(
            WorkerVerificationDocument.objects.filter(
                helper__user=self.helper,
                document_type=WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
                is_current=True,
            ).exists()
        )

    def test_verification_page_shows_profile_photo_ready_when_on_user_account(self):
        from website.tests.media_fixtures import tiny_png

        profile = HelperProfile.objects.get(user=self.helper)
        profile.profile_photo = None
        profile.save(update_fields=["profile_photo"])
        self.helper.profile_photo.save("reg.png", tiny_png(), save=True)
        HelperTrustSignal.objects.filter(
            helper=profile,
            signal_type=HelperTrustSignal.SignalType.PROFILE_PHOTO,
        ).update(status=HelperTrustSignal.SignalStatus.NOT_PROVIDED)

        self.client.force_login(self.helper)
        response = self.client.get(reverse("worker_portal:verification"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile photo")
        self.assertContains(response, "Ready")
        self.assertNotContains(response, "Not provided")

    def test_employer_cannot_access_verification_upload(self):
        self.client.force_login(self.employer)
        response = self.client.post(
            reverse("worker_portal:verification_upload"),
            data={
                "document_type": WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
                "file": SimpleUploadedFile("id.pdf", MINIMAL_PDF, content_type="application/pdf"),
            },
        )
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)
