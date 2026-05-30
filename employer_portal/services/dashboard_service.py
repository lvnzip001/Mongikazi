from django.forms import ValidationError
from django.urls import reverse

from employers.models import EmployerTrustSignal
from employers.services.onboarding_handoff_service import create_or_update_employer_profile_from_onboarding

from bookings.selectors.employer_opportunities_selectors import get_employer_opportunities_context
from messaging.selectors.messaging_selectors import get_recent_unread_threads_for_user
from employer_portal.selectors.portal_selectors import (
    get_available_service_categories,
    get_employer_portal_primary_location,
    get_employer_portal_profile,
    get_employer_portal_service_preference,
    get_helper_teasers,
)


def _teaser_service_labels(helper):
    skills = list(helper.skills.all())
    if not skills:
        return []
    names = [skill.category.name for skill in skills if getattr(skill, "category", None)]
    return names[:2]


def build_employer_dashboard_context(user):
    if not getattr(user, "is_employer", False):
        raise ValidationError("Employer portal is only available to employer users.")

    employer_profile = get_employer_portal_profile(user)
    if not employer_profile:
        try:
            employer_profile = create_or_update_employer_profile_from_onboarding(user)
        except ValidationError:
            employer_profile = None

    primary_location = None
    service_preference = None
    trust_signals = []
    profile_completion_percent = 0
    trust_status_display = "New"

    if employer_profile:
        primary_location = get_employer_portal_primary_location(employer_profile)
        service_preference = get_employer_portal_service_preference(employer_profile)
        trust_signals = list(employer_profile.trust_signals.all())
        profile_completion_percent = employer_profile.profile_completion_percent
        trust_status_display = employer_profile.get_trust_status_display()

    categories = list(get_available_service_categories())
    teaser_profiles = list(get_helper_teasers(limit=4))
    helper_teasers = [
        {
            "display_name": profile.display_name or profile.user.first_name or "Helper",
            "location": profile.location,
            "trust_status": profile.get_trust_status_display(),
            "is_verified": profile.is_verified,
            "services": _teaser_service_labels(profile),
        }
        for profile in teaser_profiles
    ]

    opportunities = get_employer_opportunities_context(user, preview_limit=3)
    placeholder_counts = opportunities["counts"]

    next_actions = []
    if not employer_profile:
        next_actions.append({"title": "Complete employer profile", "url": "/employers/profile/"})
    else:
        if not primary_location:
            next_actions.append({"title": "Add your primary location", "url": "/employers/profile/locations/"})
        if not service_preference:
            next_actions.append({"title": "Set your service preferences", "url": "/employers/profile/preferences/"})
        if employer_profile.profile_completion_percent < 70:
            next_actions.append({"title": "Increase booking readiness", "url": "/employers/profile/incomplete/"})

    if not next_actions:
        next_actions.append({"title": "Start finding trusted help", "url": "/employer/find-help/"})

    service_need_summary = None
    if service_preference:
        service_need_summary = {
            "service_type": service_preference.get_service_type_display(),
            "service_frequency": service_preference.get_service_frequency_display(),
            "preferred_time": service_preference.preferred_time,
        }

    dashboard_alerts = []
    if opportunities["counts"]["pending_response"]:
        dashboard_alerts.append(
            {
                "message": f"{opportunities['counts']['pending_response']} booking(s) awaiting worker response.",
                "url": reverse("bookings:employer_bookings"),
            }
        )
    if opportunities["counts"]["applications_received"]:
        dashboard_alerts.append(
            {
                "message": f"{opportunities['counts']['applications_received']} job(s) have new applications to review.",
                "url": reverse("bookings:employer_marketplace_jobs"),
            }
        )
    if opportunities["counts"]["messages"]:
        dashboard_alerts.append(
            {
                "message": f"You have {opportunities['counts']['messages']} unread message(s).",
                "url": reverse("messaging:inbox"),
            }
        )

    return {
        "profile": employer_profile,
        "profile_completion_percent": profile_completion_percent,
        "trust_status_display": trust_status_display,
        "primary_location": primary_location,
        "service_preference": service_preference,
        "service_need_summary": service_need_summary,
        "service_categories": categories,
        "helper_teasers": helper_teasers,
        "placeholder_counts": placeholder_counts,
        "next_actions": next_actions,
        "trust_signal_count": len(trust_signals),
        "ready_signal_count": len([s for s in trust_signals if s.status == EmployerTrustSignal.SignalStatus.READY]),
        "greeting_name": user.first_name or user.username,
        "pending_response_preview": opportunities["pending_response"],
        "confirmed_upcoming_preview": opportunities["confirmed_upcoming"],
        "applications_received_preview": opportunities["applications_received"],
        "unread": opportunities["unread"],
        "recent_unread_threads": get_recent_unread_threads_for_user(user, limit=2),
        "dashboard_alerts": dashboard_alerts,
    }