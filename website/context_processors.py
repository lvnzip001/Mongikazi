from django.urls import reverse


def portal_navigation(request):
    """Shared portal URLs and active nav hints for profile shells."""
    ctx = {
        "work_profile_url": reverse("helpers:profile_detail"),
        "employer_profile_url": reverse("employers:profile_detail"),
        "worker_dashboard_url": reverse("worker_portal:dashboard"),
        "employer_dashboard_url": reverse("employer_portal:dashboard"),
    }

    match = getattr(request, "resolver_match", None)
    if not match:
        return ctx

    if match.app_name == "helpers":
        ctx["nav_active"] = "profile"
        ctx["profile_nav_active"] = match.url_name
        ctx["portal_section"] = "worker"
    elif match.app_name == "employers":
        ctx["nav_active"] = "profile"
        ctx["profile_nav_active"] = match.url_name
        ctx["portal_section"] = "employer"
    elif match.app_name == "payments" and match.url_name:
        if match.url_name.startswith("worker"):
            ctx["nav_active"] = "earnings"
        elif match.url_name.startswith("employer"):
            ctx["nav_active"] = "payments"
        elif match.url_name == "operations_payments_review":
            ctx["nav_active"] = "operations_review"
        elif match.url_name == "operations_payout_history":
            ctx["nav_active"] = "operations_payout_history"

    return ctx


def portal_nav_counts(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"portal_nav_counts": {}}

    from bookings.models import Booking
    from bookings.selectors.booking_selectors import get_employer_bookings, get_worker_booking_requests

    counts = {}
    if getattr(user, "is_helper", False):
        counts["offers"] = get_worker_booking_requests(user).count()
    if getattr(user, "is_employer", False):
        counts["pending_response"] = (
            get_employer_bookings(user).filter(status=Booking.Status.PENDING_WORKER_RESPONSE).count()
        )
        counts["applications_received"] = (
            get_employer_bookings(user).filter(status=Booking.Status.APPLICATIONS_RECEIVED).count()
        )
    return {"portal_nav_counts": counts}
