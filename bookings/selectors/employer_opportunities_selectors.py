from django.urls import reverse

from bookings.models import Booking
from bookings.selectors.booking_selectors import get_employer_bookings, get_employer_marketplace_jobs
from employers.selectors.employer_selectors import get_employer_profile_for_user
from helpers.selectors.verification_selectors import build_employer_safe_worker_card
from messaging.selectors.messaging_selectors import get_booking_thread_unread_count, get_recent_unread_threads_for_user, get_unread_counts_for_user


def _service_area(booking):
    if booking.employer_location_id:
        return booking.employer_location.service_area_display()
    return ""


def build_employer_booking_row(booking, user):
    worker_card = build_employer_safe_worker_card(booking.worker) if booking.worker_id else None
    return {
        "booking": booking,
        "worker_card": worker_card,
        "service_area": _service_area(booking),
        "unread_count": get_booking_thread_unread_count(booking, user),
        "detail_url": reverse("bookings:employer_booking_detail", kwargs={"booking_reference": booking.booking_reference}),
        "applications_url": reverse(
            "bookings:employer_booking_applications",
            kwargs={"booking_reference": booking.booking_reference},
        ),
    }


def get_employer_opportunities_context(user, preview_limit=3):
    unread = get_unread_counts_for_user(user)
    employer_profile = get_employer_profile_for_user(user)
    if not employer_profile:
        return {
            "pending_response": [],
            "confirmed_upcoming": [],
            "applications_received": [],
            "past_bookings": [],
            "counts": {
                "pending_response": 0,
                "confirmed_upcoming": 0,
                "applications_received": 0,
                "bookings": 0,
                "messages": 0,
            },
            "unread": unread,
            "recent_unread_threads": [],
        }

    base_qs = (
        get_employer_bookings(user)
        .select_related("worker", "worker__user", "service_category", "employer_location", "employer_location__locality")
        .order_by("scheduled_date", "start_time")
    )

    pending_qs = list(base_qs.filter(status=Booking.Status.PENDING_WORKER_RESPONSE))
    confirmed_qs = list(base_qs.filter(status__in=[Booking.Status.ACCEPTED, Booking.Status.IN_PROGRESS]))
    applications_received_qs = list(
        get_employer_marketplace_jobs(user).filter(status=Booking.Status.APPLICATIONS_RECEIVED).order_by("-created_at")
    )
    past_qs = list(
        base_qs.filter(
            status__in=[
                Booking.Status.COMPLETED,
                Booking.Status.DECLINED,
                Booking.Status.CANCELLED_BY_EMPLOYER,
                Booking.Status.CANCELLED_BY_WORKER,
                Booking.Status.CLOSED,
            ]
        ).order_by("-scheduled_date", "-start_time")[:20]
    )

    pending_response = [build_employer_booking_row(b, user) for b in pending_qs]
    confirmed_upcoming = [build_employer_booking_row(b, user) for b in confirmed_qs]
    applications_received = [build_employer_booking_row(b, user) for b in applications_received_qs]

    counts = {
        "pending_response": len(pending_qs),
        "confirmed_upcoming": len(confirmed_qs),
        "applications_received": len(applications_received_qs),
        "bookings": len(pending_qs) + len(confirmed_qs),
        "messages": unread["total_unread"],
        "favourites": 0,
        "payments": 0,
    }

    return {
        "pending_response": pending_response[:preview_limit],
        "pending_response_all": pending_response,
        "confirmed_upcoming": confirmed_upcoming[:preview_limit],
        "confirmed_upcoming_all": confirmed_upcoming,
        "applications_received": applications_received[:preview_limit],
        "applications_received_all": applications_received,
        "past_bookings": [build_employer_booking_row(b, user) for b in past_qs],
        "counts": counts,
        "unread": unread,
        "recent_unread_threads": get_recent_unread_threads_for_user(user, limit=preview_limit),
        "employer_profile": employer_profile,
    }
