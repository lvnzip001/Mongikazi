from django.forms import ValidationError
from django.urls import reverse

from helpers.models import HelperTrustSignal
from helpers.services.onboarding_handoff_service import create_or_update_helper_profile_from_onboarding

from bookings.selectors.worker_opportunities_selectors import get_worker_opportunities_context
from messaging.selectors.messaging_selectors import get_recent_unread_threads_for_user
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

    opportunities = get_worker_opportunities_context(user, preview_limit=3)
    placeholder_counts = opportunities["counts"]

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

    dashboard_alerts = []
    if opportunities["counts"]["offers"]:
        dashboard_alerts.append(
            {
                "message": f"You have {opportunities['counts']['offers']} new offer(s) awaiting your response.",
                "url": reverse("worker_portal:offers"),
            }
        )
    if opportunities["counts"]["unread_messages"]:
        dashboard_alerts.append(
            {
                "message": f"You have {opportunities['counts']['unread_messages']} unread message(s).",
                "url": reverse("messaging:inbox"),
            }
        )

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
        "new_offers_preview": opportunities["new_offers"][:3],
        "upcoming_jobs_preview": opportunities["upcoming_jobs"],
        "available_jobs_preview": opportunities["available_jobs_preview"],
        "pending_applications_count": opportunities["pending_applications_count"],
        "available_jobs_count": opportunities["available_jobs_count"],
        "unread": opportunities["unread"],
        "recent_unread_threads": get_recent_unread_threads_for_user(user, limit=2),
        "dashboard_alerts": dashboard_alerts,
    }