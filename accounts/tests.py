from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import RegisterForm
from .models import User
from .services.redirect_service import get_onboarding_url, get_role_redirect_url


class AccountsModelTests(TestCase):
    def test_user_role_helpers(self):
        user = User.objects.create_user(
            username="helper@example.com",
            email="helper@example.com",
            password="safe-password-123",
            role=User.Role.HELPER,
            phone_number="0710000001",
        )
        self.assertTrue(user.is_helper)
        self.assertFalse(user.is_employer)

    def test_permission_related_names_do_not_use_default_user_set(self):
        groups_field = User._meta.get_field("groups")
        permissions_field = User._meta.get_field("user_permissions")
        self.assertEqual(groups_field.remote_field.related_name, "mongikazi_user_set")
        self.assertEqual(permissions_field.remote_field.related_name, "mongikazi_user_set")


class AccountsAuthFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"

    def test_employer_registration_creates_user(self):
        response = self.client.post(
            reverse("accounts:register", kwargs={"role": "employer"}),
            {
                "first_name": "Emp",
                "last_name": "Loyer",
                "email": "emp@example.com",
                "phone_number": "071 000 0001",
                "password1": self.password,
                "password2": self.password,
                "accepted_terms": True,
            },
        )
        user = User.objects.get(email="emp@example.com")
        self.assertEqual(user.role, User.Role.EMPLOYER)
        self.assertIsNotNone(user.accepted_terms_at)
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_registration_without_email_uses_phone_as_username(self):
        response = self.client.post(
            reverse("accounts:register", kwargs={"role": "helper"}),
            {
                "first_name": "No",
                "last_name": "Email",
                "email": "",
                "phone_number": "071 000 0099",
                "password1": self.password,
                "password2": self.password,
                "accepted_terms": True,
            },
        )
        user = User.objects.get(phone_number="0710000099")
        self.assertIsNone(user.email)
        self.assertEqual(user.username, "0710000099")
        self.assertEqual(user.role, User.Role.HELPER)
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

        login_response = self.client.post(
            reverse("accounts:login"),
            {"identifier": "0710000099", "password": self.password},
        )
        self.assertRedirects(login_response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_helper_registration_creates_user(self):
        response = self.client.post(
            reverse("accounts:register", kwargs={"role": "helper"}),
            {
                "first_name": "Help",
                "last_name": "Er",
                "email": "helper@example.com",
                "phone_number": "071-000-0002",
                "password1": self.password,
                "password2": self.password,
                "accepted_terms": True,
            },
        )
        user = User.objects.get(email="helper@example.com")
        self.assertEqual(user.role, User.Role.HELPER)
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_duplicate_email_validation_is_case_insensitive(self):
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            phone_number="0710000003",
            password=self.password,
            role=User.Role.EMPLOYER,
        )
        form = RegisterForm(
            data={
                "first_name": "A",
                "last_name": "B",
                "email": "Existing@Example.Com",
                "phone_number": "0710000004",
                "password1": self.password,
                "password2": self.password,
                "accepted_terms": True,
            },
            role=User.Role.EMPLOYER,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_duplicate_phone_validation_after_normalization(self):
        User.objects.create_user(
            username="phone@example.com",
            email="phone@example.com",
            phone_number="+27710000005",
            password=self.password,
            role=User.Role.HELPER,
        )
        form = RegisterForm(
            data={
                "first_name": "A",
                "last_name": "B",
                "email": "new@example.com",
                "phone_number": "+27 71-000-0005",
                "password1": self.password,
                "password2": self.password,
                "accepted_terms": True,
            },
            role=User.Role.HELPER,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_login_works_with_email(self):
        User.objects.create_user(
            username="login-email@example.com",
            email="login-email@example.com",
            phone_number="0710000006",
            password=self.password,
            role=User.Role.EMPLOYER,
        )
        response = self.client.post(reverse("accounts:login"), {"identifier": "login-email@example.com", "password": self.password})
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_login_works_with_phone_number(self):
        User.objects.create_user(
            username="login-phone@example.com",
            email="login-phone@example.com",
            phone_number="0710000007",
            password=self.password,
            role=User.Role.HELPER,
        )
        response = self.client.post(reverse("accounts:login"), {"identifier": "071 000 0007", "password": self.password})
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    def test_incomplete_employer_redirects_to_onboarding_start(self):
        user = User.objects.create_user(
            username="employer1@example.com",
            email="employer1@example.com",
            phone_number="0710000008",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=False,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:role_select"))
        self.assertRedirects(response, reverse("onboarding:start"), fetch_redirect_response=False)

    @override_settings(MONGIKAZI_EMPLOYER_PORTAL_URL="/employer/dashboard/")
    def test_completed_employer_redirects_to_settings_portal_url(self):
        user = User.objects.create_user(
            username="employer2@example.com",
            email="employer2@example.com",
            phone_number="0710000009",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:role_select"))
        self.assertRedirects(response, "/employer/dashboard/", fetch_redirect_response=False)

    @override_settings(MONGIKAZI_HELPER_PORTAL_URL="/helper/dashboard/")
    def test_completed_helper_redirects_to_settings_portal_url(self):
        user = User.objects.create_user(
            username="helper2@example.com",
            email="helper2@example.com",
            phone_number="0710000010",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:role_select"))
        self.assertRedirects(response, "/helper/dashboard/", fetch_redirect_response=False)

    @override_settings(MONGIKAZI_OPERATIONS_PORTAL_URL="/operations/console/")
    def test_staff_redirects_to_operations_url_setting(self):
        user = User.objects.create_user(
            username="ops@example.com",
            email="ops@example.com",
            phone_number="0710000011",
            password=self.password,
            role=User.Role.HELPER,
            is_staff=True,
            is_onboarding_complete=True,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:role_select"))
        self.assertRedirects(response, "/operations/console/", fetch_redirect_response=False)

    def test_unsafe_next_url_is_ignored(self):
        user = User.objects.create_user(
            username="unsafe@example.com",
            email="unsafe@example.com",
            phone_number="0710000012",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        response = self.client.post(
            reverse("accounts:login"),
            {"identifier": user.email, "password": self.password, "next": "https://evil.example.com/phish"},
        )
        self.assertRedirects(response, "/employer/", fetch_redirect_response=False)

    def test_safe_next_url_is_honoured(self):
        user = User.objects.create_user(
            username="safe@example.com",
            email="safe@example.com",
            phone_number="0710000013",
            password=self.password,
            role=User.Role.EMPLOYER,
            is_onboarding_complete=True,
        )
        response = self.client.post(
            reverse("accounts:login"),
            {"identifier": user.email, "password": self.password, "next": "/requested/page/"},
        )
        self.assertRedirects(response, "/requested/page/", fetch_redirect_response=False)

    def test_completed_helper_default_redirect_goes_to_worker_portal(self):
        user = User.objects.create_user(
            username="helper-default@example.com",
            email="helper-default@example.com",
            phone_number="0710000015",
            password=self.password,
            role=User.Role.HELPER,
            is_onboarding_complete=True,
        )
        response = self.client.post(
            reverse("accounts:login"),
            {"identifier": user.email, "password": self.password},
        )
        self.assertRedirects(response, "/worker/", fetch_redirect_response=False)

    def test_logout_requires_post(self):
        user = User.objects.create_user(
            username="logout@example.com",
            email="logout@example.com",
            phone_number="0710000014",
            password=self.password,
            role=User.Role.HELPER,
        )
        self.client.force_login(user)
        get_response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(get_response.status_code, 405)

        post_response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(post_response.status_code, 302)

    def test_password_reset_placeholder_renders(self):
        response = self.client.get(reverse("accounts:password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password reset")


class RedirectServiceTests(TestCase):
    def test_incomplete_employer_goes_to_onboarding_start(self):
        user = User(username="employer@example.com", role=User.Role.EMPLOYER, is_onboarding_complete=False)
        self.assertEqual(get_role_redirect_url(user), reverse("onboarding:start"))
        self.assertEqual(get_onboarding_url(user), reverse("onboarding:start"))




