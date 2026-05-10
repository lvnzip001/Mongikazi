from django.utils import timezone

from accounts.models import User

from onboarding.models import EmployerOnboardingProfile, HelperOnboardingProfile


def user_can_access_employer_onboarding(user):
    return user.is_authenticated and user.role == User.Role.EMPLOYER


def user_can_access_helper_onboarding(user):
    return user.is_authenticated and user.role == User.Role.HELPER


def get_or_create_employer_onboarding_profile(user):
    profile, _ = EmployerOnboardingProfile.objects.get_or_create(user=user)
    return profile


def get_or_create_helper_onboarding_profile(user):
    profile, _ = HelperOnboardingProfile.objects.get_or_create(user=user)
    return profile


def complete_employer_onboarding(user):
    profile = get_or_create_employer_onboarding_profile(user)
    if not profile.is_completed:
        profile.is_completed = True
        profile.completed_at = timezone.now()
        profile.save(update_fields=["is_completed", "completed_at", "updated_at"])

    if not user.is_onboarding_complete:
        user.is_onboarding_complete = True
        user.save(update_fields=["is_onboarding_complete"])
    return profile


def complete_helper_onboarding(user):
    profile = get_or_create_helper_onboarding_profile(user)
    if not profile.is_completed:
        profile.is_completed = True
        profile.completed_at = timezone.now()
        profile.save(update_fields=["is_completed", "completed_at", "updated_at"])

    if not user.is_onboarding_complete:
        user.is_onboarding_complete = True
        user.save(update_fields=["is_onboarding_complete"])
    return profile
