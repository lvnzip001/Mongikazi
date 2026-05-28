from django.conf import settings
from django.urls import NoReverseMatch, reverse


def get_public_home_url():
    """Return a safe public-home fallback that does not depend on website URLs."""
    return getattr(settings, "MONGIKAZI_PUBLIC_HOME_URL", "/")


def get_portal_url(user):
    """Return the final portal destination for a fully onboarded user."""
    if not user.is_authenticated:
        return reverse("accounts:login")

    if user.is_staff or user.is_superuser or getattr(user, "is_operations_user", False):
        return getattr(settings, "MONGIKAZI_OPERATIONS_PORTAL_URL", "/operations/")

    if getattr(user, "is_employer", False):
        return getattr(settings, "MONGIKAZI_EMPLOYER_PORTAL_URL", "/employer/")

    if getattr(user, "is_helper", False):
        return getattr(settings, "MONGIKAZI_HELPER_PORTAL_URL", "/worker/")

    return reverse("accounts:role_select")


def get_onboarding_url(user):
    """Return onboarding start URL with a safe fallback."""
    try:
        return reverse("onboarding:start")
    except NoReverseMatch:
        return "/onboarding/start/"


def get_role_redirect_url(user):
    """Return the correct post-login destination for a MongiKazi user."""
    if not user.is_authenticated:
        return reverse("accounts:login")

    if user.is_staff or user.is_superuser or getattr(user, "is_operations_user", False):
        return get_portal_url(user)

    if getattr(user, "is_employer", False) or getattr(user, "is_helper", False):
        if not user.is_onboarding_complete:
            return get_onboarding_url(user)
        return get_portal_url(user)

    return reverse("accounts:role_select")
