from django.forms import ValidationError

from helpers.models import HelperTrustSignal
from helpers.services.onboarding_handoff_service import create_or_update_helper_profile_from_onboarding

from worker_portal.selectors.portal_selectors import (
    get_worker_portal_availability,
    get_worker_portal_profile,
    get_worker_portal_skills,
    get_worker_portal_trust_signals,
)


def _skills_summary(skills):
    names = [skill.category.name for skill in skills if getattr(skill, "category", None)]
    return names[:4]


def _availability_summary(helper_profile, availability_rows):
    if helper_profile and helper_profile.availability_summary:
        return helper_profile.availability_summary
    if availability_rows:
        first = availability_rows[0]
        return f"{first.get_day_of_week_display()} {first.start_time.strftime('%H:%M')}-{first.end_time.strftime('%H:%M')}"
    return "Availability not set"


def build_worker_dashboard_context(user):
    if not getattr(user, "is_helper", False):
        raise ValidationError("Worker portal is only available to helper users.")

    helper_profile = get_worker_portal_profile(user)
    if not helper_profile:
        try:
            helper_profile = create_or_update_helper_profile_from_onboarding(user)
        except ValidationError:
            helper_profile = None

    skills = []
    availability_rows = []
    trust_signals = []
    profile_completion_percent = 0
    trust_status_display = "New"

    if helper_profile:
        skills = list(get_worker_portal_skills(helper_profile))
        availability_rows = list(get_worker_portal_availability(helper_profile))
        trust_signals = list(get_worker_portal_trust_signals(helper_profile))
        profile_completion_percent = helper_profile.profile_completion_percent
        trust_status_display = helper_profile.get_trust_status_display()

    placeholder_counts = {
        "requests": 0,
        "jobs": 0,
        "messages": 0,
        "reviews": 0,
    }

    earnings_summary = {
        "weekly_total": "R0",
        "status": "Earnings activate after completed jobs",
    }

    services = _skills_summary(skills)
    availability_summary = _availability_summary(helper_profile, availability_rows)

    next_actions = []
    if not helper_profile:
        next_actions.append({"title": "Complete work profile", "url": "/helpers/profile/"})
    else:
        if not skills:
            next_actions.append({"title": "Add service skills", "url": "/helpers/profile/skills/"})
        if not (helper_profile.availability_summary or availability_rows):
            next_actions.append({"title": "Set availability", "url": "/helpers/profile/availability/"})
        if helper_profile.profile_completion_percent < 70:
            next_actions.append({"title": "Increase profile readiness", "url": "/helpers/profile/incomplete/"})

    if not next_actions:
        next_actions.append({"title": "Preview your work profile", "url": "/helpers/profile/preview/"})

    return {
        "profile": helper_profile,
        "profile_completion_percent": profile_completion_percent,
        "trust_status_display": trust_status_display,
        "skills": skills,
        "services": services,
        "availability_rows": availability_rows,
        "availability_summary": availability_summary,
        "trust_signals": trust_signals,
        "placeholder_counts": placeholder_counts,
        "earnings_summary": earnings_summary,
        "next_actions": next_actions,
        "trust_signal_count": len(trust_signals),
        "ready_signal_count": len([s for s in trust_signals if s.status == HelperTrustSignal.SignalStatus.READY]),
        "greeting_name": user.first_name or user.username,
    }