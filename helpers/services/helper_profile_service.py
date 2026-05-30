from django.forms import ValidationError

from helpers.models import HelperProfile
from helpers.services.onboarding_handoff_service import create_or_update_helper_profile_from_onboarding
from helpers.services.profile_completion_service import calculate_helper_profile_completion
from helpers.services.verification_service import sync_verification_trust_signals


def get_or_create_helper_profile_for_user(user):
    if not getattr(user, "is_helper", False):
        raise ValidationError("Only helper users can have helper profiles.")

    profile = HelperProfile.objects.filter(user=user).first()
    if profile:
        return profile

    return create_or_update_helper_profile_from_onboarding(user)


def refresh_helper_profile_state(profile):
    sync_verification_trust_signals(profile)
    calculate_helper_profile_completion(profile)
    profile.refresh_from_db()
    return profile
