from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase

from accounts.models import User
from website.profile_photos import (
    avatar_context,
    profile_initials,
    profile_photo_url,
    validate_profile_photo,
)
from website.tests.media_fixtures import MINIMAL_PNG, tiny_png


class ProfilePhotoValidationTests(SimpleTestCase):
    def test_rejects_oversized_upload(self):
        upload = SimpleUploadedFile("big.jpg", b"x" * (5 * 1024 * 1024 + 1), content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            validate_profile_photo(upload)

    def test_accepts_small_png(self):
        validate_profile_photo(tiny_png())


class ProfilePhotoDisplayTests(TestCase):
    def test_initials_from_display_name(self):
        class Subject:
            display_name = "Jane Doe"
            profile_photo = None
            user = None

        self.assertEqual(profile_initials(Subject()), "JD")

    def test_avatar_context_falls_back_to_user_photo(self):
        user = User.objects.create_user(
            username="photo@example.com",
            email="photo@example.com",
            password="safe-password-123",
            role=User.Role.HELPER,
        )
        user.profile_photo.save("avatar.png", tiny_png(), save=True)

        subject = type(
            "Subject",
            (),
            {"display_name": "Helper One", "profile_photo": None, "user": user},
        )()

        ctx = avatar_context(subject, size="md")
        self.assertTrue(ctx["photo_url"])
        self.assertEqual(ctx["initials"], "HO")
        self.assertEqual(profile_photo_url(subject), ctx["photo_url"])


class ProfileAvatarTemplateTagTests(TestCase):
    def test_profile_avatar_renders_photo_markup(self):
        user = User.objects.create_user(
            username="tag@example.com",
            email="tag@example.com",
            password="safe-password-123",
            role=User.Role.HELPER,
        )
        user.profile_photo.save("tag.png", tiny_png(), save=True)
        profile = type(
            "Profile",
            (),
            {"display_name": "Tag User", "profile_photo": None, "user": user},
        )()
        rendered = Template(
            "{% load profile_display %}{% profile_avatar profile size='md' %}"
        ).render(Context({"profile": profile}))
        self.assertIn("mk-avatar--photo", rendered)
        self.assertIn(profile_photo_url(profile), rendered)

    def test_profile_avatar_renders_initials_without_photo(self):
        profile = type("Profile", (), {"display_name": "Sam Lee", "profile_photo": None, "user": None})()
        rendered = Template(
            "{% load profile_display %}{% profile_avatar profile size='sm' %}"
        ).render(Context({"profile": profile}))
        self.assertIn("mk-avatar__initials", rendered)
        self.assertIn("SL", rendered)
