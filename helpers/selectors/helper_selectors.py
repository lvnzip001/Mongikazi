from helpers.models import HelperAvailability, HelperProfile, HelperSkill, HelperTrustSignal


def get_helper_profile_for_user(user):
    return HelperProfile.objects.filter(user=user).first()


def get_active_helper_profiles():
    return HelperProfile.objects.filter(is_active=True).select_related("user")


def get_helper_skills(helper_profile):
    return HelperSkill.objects.filter(helper=helper_profile).select_related("category")


def get_helper_availability(helper_profile):
    return HelperAvailability.objects.filter(helper=helper_profile)


def get_helper_trust_signals(helper_profile):
    return HelperTrustSignal.objects.filter(helper=helper_profile)


def get_helper_profile_preview_context(helper_profile):
    skills = list(get_helper_skills(helper_profile))
    trust_signals = list(get_helper_trust_signals(helper_profile))
    return {
        "helper": helper_profile,
        "skills": skills,
        "trust_signals": trust_signals,
        "services": [skill.category.name for skill in skills],
    }
