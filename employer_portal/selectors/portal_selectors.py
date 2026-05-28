from employers.selectors.employer_selectors import (
    get_employer_profile_for_user,
    get_employer_service_preferences,
    get_primary_employer_location,
)
from helpers.models import HelperProfile, ServiceCategory


def get_employer_portal_profile(user):
    return get_employer_profile_for_user(user)


def get_employer_portal_primary_location(employer_profile):
    return get_primary_employer_location(employer_profile)


def get_employer_portal_service_preference(employer_profile):
    return get_employer_service_preferences(employer_profile).first()


def get_available_service_categories():
    return ServiceCategory.objects.filter(is_active=True).order_by("sort_order", "name")


def get_helper_teasers(limit=4):
    return (
        HelperProfile.objects.filter(is_active=True)
        .select_related("user")
        .prefetch_related("skills__category")
        .order_by("-is_verified", "-profile_completion_percent", "-updated_at")[:limit]
    )