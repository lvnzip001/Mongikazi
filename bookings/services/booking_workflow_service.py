from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, BookingEvent
from bookings.services.booking_event_service import create_booking_event
from payments.services.payment_service import issue_invoice_for_completed_booking


def _is_worker_actor(booking, user):
    return bool(user and booking.worker and booking.worker.user_id == user.id)


def _is_employer_actor(booking, user):
    return bool(user and booking.employer and booking.employer.user_id == user.id)


def _assert_allowed_status(booking, allowed_statuses, action_label):
    if booking.status not in allowed_statuses:
        allowed_display = ", ".join(allowed_statuses)
        raise ValidationError(f"Booking cannot be {action_label} from status '{booking.status}'. Allowed: {allowed_display}.")


def _transition_booking(booking, *, to_status, performed_by, event_type, description="", metadata=None):
    from_status = booking.status
    booking.status = to_status
    if to_status == Booking.Status.COMPLETED:
        booking.completed_at = timezone.now()
    booking.save(update_fields=["status", "completed_at", "decline_reason", "cancel_reason", "updated_at"])
    create_booking_event(
        booking=booking,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        description=description,
        performed_by=performed_by,
        metadata=metadata,
    )
    return booking


@transaction.atomic
def accept_booking(booking, performed_by):
    if not _is_worker_actor(booking, performed_by):
        raise ValidationError("Only the assigned worker can accept this booking.")
    _assert_allowed_status(booking, [Booking.Status.PENDING_WORKER_RESPONSE], "accepted")
    return _transition_booking(
        booking,
        to_status=Booking.Status.ACCEPTED,
        performed_by=performed_by,
        event_type=BookingEvent.EventType.WORKER_ACCEPTED,
        description="Worker accepted booking request.",
    )


@transaction.atomic
def decline_booking(booking, performed_by, reason=""):
    if not _is_worker_actor(booking, performed_by):
        raise ValidationError("Only the assigned worker can decline this booking.")
    _assert_allowed_status(booking, [Booking.Status.PENDING_WORKER_RESPONSE], "declined")
    booking.decline_reason = reason.strip()
    return _transition_booking(
        booking,
        to_status=Booking.Status.DECLINED,
        performed_by=performed_by,
        event_type=BookingEvent.EventType.WORKER_DECLINED,
        description="Worker declined booking request.",
        metadata={"reason": booking.decline_reason},
    )


@transaction.atomic
def cancel_booking_by_employer(booking, performed_by, reason=""):
    if not _is_employer_actor(booking, performed_by):
        raise ValidationError("Only the booking employer can cancel this booking.")
    _assert_allowed_status(
        booking,
        [Booking.Status.PENDING_WORKER_RESPONSE, Booking.Status.ACCEPTED],
        "cancelled",
    )
    booking.cancel_reason = reason.strip()
    return _transition_booking(
        booking,
        to_status=Booking.Status.CANCELLED_BY_EMPLOYER,
        performed_by=performed_by,
        event_type=BookingEvent.EventType.EMPLOYER_CANCELLED,
        description="Employer cancelled booking.",
        metadata={"reason": booking.cancel_reason},
    )


@transaction.atomic
def cancel_booking_by_worker(booking, performed_by, reason=""):
    if not _is_worker_actor(booking, performed_by):
        raise ValidationError("Only the assigned worker can cancel this booking.")
    _assert_allowed_status(booking, [Booking.Status.ACCEPTED], "cancelled")
    booking.cancel_reason = reason.strip()
    return _transition_booking(
        booking,
        to_status=Booking.Status.CANCELLED_BY_WORKER,
        performed_by=performed_by,
        event_type=BookingEvent.EventType.WORKER_CANCELLED,
        description="Worker cancelled accepted booking.",
        metadata={"reason": booking.cancel_reason},
    )


@transaction.atomic
def mark_booking_completed(booking, performed_by):
    if not _is_employer_actor(booking, performed_by):
        raise ValidationError("Only the booking employer can mark this booking as completed.")
    _assert_allowed_status(booking, [Booking.Status.ACCEPTED], "completed")
    booking = _transition_booking(
        booking,
        to_status=Booking.Status.COMPLETED,
        performed_by=performed_by,
        event_type=BookingEvent.EventType.MARKED_COMPLETED,
        description="Employer marked booking as completed.",
    )
    issue_invoice_for_completed_booking(booking)
    return booking
