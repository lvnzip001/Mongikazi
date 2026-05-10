from django.urls import reverse

from accounts.models import User

from onboarding.services.onboarding_service import (
    get_or_create_employer_onboarding_profile,
    get_or_create_helper_onboarding_profile,
)


def redirect_user_to_correct_onboarding_flow(user):
    if user.role == User.Role.EMPLOYER:
        profile = get_or_create_employer_onboarding_profile(user)
        if user.is_onboarding_complete or profile.is_completed:
            return reverse("accounts:account_pending")
        if not profile.service_type or not profile.service_frequency:
            return reverse("onboarding:employer_service")
        return reverse("onboarding:employer_location")

    if user.role == User.Role.HELPER:
        profile = get_or_create_helper_onboarding_profile(user)
        if user.is_onboarding_complete or profile.is_completed:
            return reverse("accounts:account_pending")
        if not profile.display_name or not profile.location or profile.years_experience is None or not profile.bio:
            return reverse("onboarding:helper_profile")
        if not profile.selected_categories or not profile.preferred_work_area or not profile.availability_summary:
            return reverse("onboarding:helper_services")
        return reverse("onboarding:helper_trust")

    return reverse("accounts:account_pending")
