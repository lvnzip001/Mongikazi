from django.urls import reverse

from bookings.models import Booking, BookingApplication
from bookings.selectors.booking_selectors import (
    get_worker_applications,
    get_worker_booking_requests,
    get_worker_jobs,
    get_worker_open_marketplace_jobs,
)
from employers.selectors.employer_selectors import build_worker_safe_employer_card
from helpers.selectors.helper_selectors import get_helper_profile_for_user
from messaging.selectors.messaging_selectors import get_booking_unread_counts_map, get_unread_counts_for_user

BOOKING_PREFETCH = (
    "employer",
    "employer__user",
    "service_category",
    "employer_location",
    "employer_location__locality",
    "worker",
)


def _instructions_snippet(booking, max_len=120):
    text = (booking.special_instructions or "").strip()
    if not text:
        return ""
    return text[:max_len] + ("…" if len(text) > max_len else "")


def _service_area(booking):
    if booking.employer_location_id:
        return booking.employer_location.service_area_display()
    return booking.employer.primary_area or ""


def build_worker_offer_row(booking, user, unread_map=None):
    employer_card = build_worker_safe_employer_card(booking.employer, booking=booking)
    unread_count = (unread_map or {}).get(booking.id, 0)
    return {
        "booking": booking,
        "employer_card": employer_card,
        "employer_display_name": employer_card["display_name"],
        "service_area": _service_area(booking),
        "instructions_snippet": _instructions_snippet(booking),
        "unread_count": unread_count,
        "detail_url": reverse("bookings:worker_request_detail", kwargs={"booking_reference": booking.booking_reference}),
        "message_url": reverse("messaging:open_booking_thread", kwargs={"booking_reference": booking.booking_reference}),
        "accept_url": reverse("bookings:worker_accept_booking", kwargs={"booking_reference": booking.booking_reference}),
        "decline_url": reverse("bookings:worker_decline_booking", kwargs={"booking_reference": booking.booking_reference}),
    }


def build_worker_opportunity_row(booking, user, unread_map=None):
    return {
        "booking": booking,
        "service_area": _service_area(booking),
        "instructions_snippet": _instructions_snippet(booking),
        "unread_count": (unread_map or {}).get(booking.id, 0),
    }


def build_worker_application_row(application, user, unread_map=None):
    booking = application.booking
    row = {
        "application": application,
        "booking": booking,
        "service_area": _service_area(booking),
        "unread_count": (unread_map or {}).get(booking.id, 0),
        "detail_url": None,
        "apply_url": reverse(
            "bookings:worker_apply_to_job",
            kwargs={"booking_reference": booking.booking_reference},
        ),
    }
    if application.status == BookingApplication.Status.SELECTED and booking.status == Booking.Status.PENDING_WORKER_RESPONSE:
        row["detail_url"] = reverse(
            "bookings:worker_request_detail",
            kwargs={"booking_reference": booking.booking_reference},
        )
    return row


def get_worker_opportunities_context(user, preview_limit=3):
    unread = get_unread_counts_for_user(user)
    new_offers_qs = list(get_worker_booking_requests(user).select_related(*BOOKING_PREFETCH).order_by("scheduled_date", "start_time"))
    available_jobs_qs = get_worker_open_marketplace_jobs(user).order_by("-created_at")
    applications_qs = list(
        get_worker_applications(user)
        .select_related("booking__employer", "booking__employer_location", "booking__service_category")
        .order_by("-created_at")
    )
    upcoming_qs = list(
        get_worker_jobs(user)
        .filter(status__in=[Booking.Status.ACCEPTED, Booking.Status.IN_PROGRESS])
        .select_related(*BOOKING_PREFETCH)
        .order_by("scheduled_date", "start_time")
    )
    history_qs = list(
        get_worker_jobs(user)
        .filter(status__in=[Booking.Status.COMPLETED, Booking.Status.CANCELLED_BY_WORKER])
        .select_related(*BOOKING_PREFETCH)
        .order_by("-scheduled_date", "-start_time")
    )

    pending_applications = [
        app
        for app in applications_qs
        if app.status in (BookingApplication.Status.PENDING, BookingApplication.Status.SHORTLISTED)
    ]
    new_offer_booking_ids = {booking.id for booking in new_offers_qs}
    selected_applications = [
        app
        for app in applications_qs
        if app.status == BookingApplication.Status.SELECTED
        and app.booking.status == Booking.Status.PENDING_WORKER_RESPONSE
        and app.booking_id not in new_offer_booking_ids
    ]

    available_jobs = list(available_jobs_qs[:preview_limit])
    unread_bookings = {b.id: b for b in new_offers_qs + upcoming_qs + available_jobs}
    for app in applications_qs:
        unread_bookings[app.booking_id] = app.booking
    unread_map = get_booking_unread_counts_map(unread_bookings.values(), user)

    new_offers = [build_worker_offer_row(b, user, unread_map) for b in new_offers_qs]
    available_jobs_preview = [build_worker_opportunity_row(b, user, unread_map) for b in available_jobs]

    counts = {
        "offers": len(new_offers_qs),
        "available_jobs": available_jobs_qs.count(),
        "pending_applications": len(pending_applications),
        "upcoming_jobs": len(upcoming_qs),
        "unread_messages": unread["total_unread"],
        "requests": len(new_offers_qs),
        "jobs": len(upcoming_qs),
        "messages": unread["total_unread"],
        "reviews": 0,
    }

    return {
        "new_offers": new_offers,
        "new_offers_all": new_offers,
        "available_jobs_preview": available_jobs_preview,
        "available_jobs_count": counts["available_jobs"],
        "pending_applications": [build_worker_application_row(a, user, unread_map) for a in pending_applications[:preview_limit]],
        "pending_applications_count": len(pending_applications),
        "selected_applications": [build_worker_application_row(a, user, unread_map) for a in selected_applications],
        "upcoming_jobs": [build_worker_opportunity_row(b, user, unread_map) for b in upcoming_qs[:preview_limit]],
        "upcoming_jobs_all": [build_worker_opportunity_row(b, user, unread_map) for b in upcoming_qs],
        "upcoming_jobs_count": len(upcoming_qs),
        "history_jobs": [build_worker_opportunity_row(b, user, unread_map) for b in history_qs],
        "counts": counts,
        "unread": unread,
        "helper_profile": get_helper_profile_for_user(user),
    }
