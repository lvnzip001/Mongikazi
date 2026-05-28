from helpers.selectors.helper_selectors import (
    get_helper_availability,
    get_helper_profile_for_user,
    get_helper_skills,
    get_helper_trust_signals,
)


def get_worker_portal_profile(user):
    return get_helper_profile_for_user(user)


def get_worker_portal_skills(helper_profile):
    return get_helper_skills(helper_profile)


def get_worker_portal_availability(helper_profile):
    return get_helper_availability(helper_profile)


def get_worker_portal_trust_signals(helper_profile):
    return get_helper_trust_signals(helper_profile)


def get_worker_portal_profile_preview_context(helper_profile):
    skills = list(get_worker_portal_skills(helper_profile))
    trust_signals = list(get_worker_portal_trust_signals(helper_profile))
    return {
        "helper": helper_profile,
        "skills": skills,
        "trust_signals": trust_signals,
        "services": [skill.category.name for skill in skills if getattr(skill, "category", None)],
    }