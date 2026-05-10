from onboarding.models import EmployerOnboardingProfile, HelperOnboardingProfile


def get_employer_onboarding_profile(user):
    return EmployerOnboardingProfile.objects.filter(user=user).first()


def get_helper_onboarding_profile(user):
    return HelperOnboardingProfile.objects.filter(user=user).first()


def get_onboarding_progress(user):
    if getattr(user, "is_employer", False):
        profile = get_employer_onboarding_profile(user)
        if not profile:
            return {"total_steps": 2, "completed_steps": 0}
        completed_steps = 0
        if profile.service_type and profile.service_frequency:
            completed_steps += 1
        if profile.preferred_location and profile.preferred_start_date and profile.preferred_time:
            completed_steps += 1
        return {"total_steps": 2, "completed_steps": completed_steps}

    if getattr(user, "is_helper", False):
        profile = get_helper_onboarding_profile(user)
        if not profile:
            return {"total_steps": 3, "completed_steps": 0}
        completed_steps = 0
        if profile.display_name and profile.location and profile.years_experience is not None and profile.bio:
            completed_steps += 1
        if profile.selected_categories and profile.preferred_work_area and profile.availability_summary:
            completed_steps += 1
        if (
            profile.has_id_document_ready is not None
            and profile.has_criminal_check_ready is not None
            and profile.has_references is not None
        ):
            completed_steps += 1
        return {"total_steps": 3, "completed_steps": completed_steps}

    return {"total_steps": 0, "completed_steps": 0}
