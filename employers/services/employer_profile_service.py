from django.forms import ValidationError

from employers.models import EmployerProfile
from employers.services.onboarding_handoff_service import create_or_update_employer_profile_from_onboarding
from employers.services.profile_completion_service import calculate_employer_profile_completion


def get_or_create_employer_profile_for_user(user):
    if not getattr(user, "is_employer", False):
        raise ValidationError("Only employer users can have employer profiles.")

    profile = EmployerProfile.objects.filter(user=user).first()
    if profile:
        return profile

    return create_or_update_employer_profile_from_onboarding(user)


def refresh_employer_profile_state(profile):
    calculate_employer_profile_completion(profile)
    profile.refresh_from_db()
    return profile