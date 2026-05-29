"""Cross-app profile photo upload and display tests."""

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from employers.models import EmployerProfile
from locations.models import Locality
from employers.services.onboarding_handoff_service import create_or_update_employer_profile_from_onboarding
from employers.services.profile_completion_service import calculate_employer_profile_completion
from helpers.models import HelperProfile
from helpers.services.onboarding_handoff_service import create_or_update_helper_profile_from_onboarding
from helpers.services.profile_completion_service import calculate_helper_profile_completion
from onboarding.models import EmployerOnboardingProfile, HelperOnboardingProfile
from website.profile_photos import profile_photo_url
from website.tests.media_fixtures import tiny_png


class HelperProfilePhotoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.locality = Locality.objects.create(
            name="Benoni",
            province="Gauteng",
            slug="benoni-gauteng-photo-helper",
            municipality="Ekurhuleni",
            locality_type=Locality.LocalityType.SUBURB,
        )

    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="helper-photo@mk.com",
            email="helper-photo@mk.com",
            phone_number="0760000101",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.profile = HelperProfile.objects.create(
            user=self.user,
            display_name="Photo Helper",
            location=self.locality.display_label,
            location_locality=self.locality,
            preferred_work_area=self.locality.display_label,
            preferred_work_area_locality=self.locality,
            bio="Reliable helper",
        )
        self.client = Client()

    def test_profile_edit_uploads_photo(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("helpers:profile_edit"),
            {
                "display_name": "Photo Helper",
                "bio": "Reliable helper",
                "years_experience": "3",
                "availability_summary": "Weekdays",
                "is_active": "on",
                "location_query": self.locality.display_label,
                "location_locality_id": str(self.locality.pk),
                "work_area_query": self.locality.display_label,
                "work_area_locality_id": str(self.locality.pk),
                "profile_photo": tiny_png("helper.png"),
            },
            format="multipart",
        )
        self.assertRedirects(response, reverse("helpers:profile_detail"), fetch_redirect_response=False)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_photo.name)
        self.assertTrue(profile_photo_url(self.profile))

    def test_profile_detail_shows_avatar_when_photo_present(self):
        self.profile.profile_photo.save("on-file.png", tiny_png(), save=True)
        self.client.force_login(self.user)
        response = self.client.get(reverse("helpers:profile_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mk-avatar--photo")
        self.assertContains(response, profile_photo_url(self.profile))

    def test_handoff_copies_user_photo_to_helper_profile(self):
        self.user.profile_photo.save("reg.png", tiny_png(), save=True)
        HelperOnboardingProfile.objects.create(
            user=self.user,
            display_name="Photo Helper",
            location="Benoni",
            years_experience=2,
            bio="Bio",
            selected_categories="cleaning",
            is_completed=True,
        )
        profile = create_or_update_helper_profile_from_onboarding(self.user)
        self.assertTrue(profile.profile_photo.name)

    def test_completion_includes_photo_points(self):
        self.profile.profile_photo.save("score.png", tiny_png(), save=True)
        percent = calculate_helper_profile_completion(self.profile)
        self.assertGreaterEqual(percent, 15)


class EmployerProfilePhotoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.locality = Locality.objects.create(
            name="Benoni",
            province="Gauteng",
            slug="benoni-gauteng-photo-employer",
            municipality="Ekurhuleni",
            locality_type=Locality.LocalityType.SUBURB,
        )

    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="employer-photo@mk.com",
            email="employer-photo@mk.com",
            phone_number="0780000101",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.profile = EmployerProfile.objects.create(
            user=self.user,
            display_name="Photo Employer",
            primary_area=self.locality.display_label,
            primary_area_locality=self.locality,
            contact_number="0780000101",
            preferred_contact_method=EmployerProfile.ContactMethod.APP,
        )
        self.client = Client()

    def test_profile_edit_uploads_photo(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("employers:profile_edit"),
            {
                "display_name": "Photo Employer",
                "employer_type": EmployerProfile.EmployerType.HOUSEHOLD,
                "primary_location_label": "Home",
                "contact_number": "0780000101",
                "preferred_contact_method": EmployerProfile.ContactMethod.APP,
                "is_active": "on",
                "primary_area_query": self.locality.display_label,
                "primary_area_locality_id": str(self.locality.pk),
                "profile_photo": tiny_png("employer.png"),
            },
            format="multipart",
        )
        self.assertRedirects(response, reverse("employers:profile_detail"), fetch_redirect_response=False)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_photo.name)

    def test_handoff_copies_user_photo_to_employer_profile(self):
        self.user.profile_photo.save("reg.png", tiny_png(), save=True)
        EmployerOnboardingProfile.objects.create(
            user=self.user,
            preferred_location="Benoni",
            service_type="cleaning",
            service_frequency="weekly",
            is_completed=True,
        )
        profile = create_or_update_employer_profile_from_onboarding(self.user)
        self.assertTrue(profile.profile_photo.name)

    def test_profile_photo_url_available_after_upload(self):
        self.profile.profile_photo.save("score.png", tiny_png(), save=True)
        self.assertTrue(profile_photo_url(self.profile))
