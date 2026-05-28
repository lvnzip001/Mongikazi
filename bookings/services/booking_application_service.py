from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, BookingApplication, BookingEvent
from bookings.services.booking_event_service import create_booking_event


def _assert_employer_owner(booking, user):
    if not user or booking.employer.user_id != user.id:
        raise ValidationError("Only the booking employer can manage applications.")


def _assert_worker_owner(worker_profile, user):
    if not user or worker_profile.user_id != user.id:
        raise ValidationError("Only the worker can perform this action.")


def _assert_open_marketplace_booking(booking):
    if booking.request_type != Booking.RequestType.OPEN_MARKETPLACE:
        raise ValidationError("This booking is not an open marketplace job.")


def _assert_application_open(booking):
    if booking.worker_id:
        raise ValidationError("Applications are closed because a worker has been selected.")
    if booking.status not in [Booking.Status.OPEN_FOR_APPLICATIONS, Booking.Status.APPLICATIONS_RECEIVED]:
        raise ValidationError("Applications are not open for this booking.")


@transaction.atomic
def apply_to_booking(*, booking, worker_profile, message="", proposed_fee=None, performed_by=None):
    _assert_open_marketplace_booking(booking)
    _assert_worker_owner(worker_profile, performed_by)
    _assert_application_open(booking)

    application, created = BookingApplication.objects.get_or_create(
        booking=booking,
        worker=worker_profile,
        defaults={
            "status": BookingApplication.Status.PENDING,
            "message": (message or "").strip(),
            "proposed_fee": proposed_fee,
        },
    )
    if not created:
        if application.status in [BookingApplication.Status.WITHDRAWN, BookingApplication.Status.DECLINED]:
            application.status = BookingApplication.Status.PENDING
            application.message = (message or "").strip()
            application.proposed_fee = proposed_fee
            application.responded_at = None
            application.save(update_fields=["status", "message", "proposed_fee", "responded_at", "updated_at"])
        else:
            raise ValidationError("You already applied to this booking.")

    if booking.status == Booking.Status.OPEN_FOR_APPLICATIONS:
        booking.status = Booking.Status.APPLICATIONS_RECEIVED
        booking.save(update_fields=["status", "updated_at"])

    create_booking_event(
        booking=booking,
        event_type=BookingEvent.EventType.WORKER_APPLIED,
        from_status="",
        to_status=booking.status,
        description="Worker applied to marketplace booking.",
        performed_by=performed_by,
        metadata={"application_id": application.id, "worker_id": worker_profile.id},
    )
    return application


@transaction.atomic
def withdraw_application(*, application, performed_by=None):
    _assert_worker_owner(application.worker, performed_by)
    if application.status in [BookingApplication.Status.SELECTED, BookingApplication.Status.DECLINED]:
        raise ValidationError("This application can no longer be withdrawn.")
    if application.status == BookingApplication.Status.WITHDRAWN:
        return application

    application.status = BookingApplication.Status.WITHDRAWN
    application.responded_at = timezone.now()
    application.save(update_fields=["status", "responded_at", "updated_at"])
    create_booking_event(
        booking=application.booking,
        event_type=BookingEvent.EventType.WORKER_WITHDREW_APPLICATION,
        description="Worker withdrew marketplace application.",
        performed_by=performed_by,
        metadata={"application_id": application.id, "worker_id": application.worker_id},
    )
    return application


@transaction.atomic
def decline_application(*, application, performed_by=None):
    booking = application.booking
    _assert_open_marketplace_booking(booking)
    _assert_employer_owner(booking, performed_by)
    if application.status in [BookingApplication.Status.DECLINED, BookingApplication.Status.SELECTED]:
        raise ValidationError("This application cannot be declined.")

    application.status = BookingApplication.Status.DECLINED
    application.responded_at = timezone.now()
    application.save(update_fields=["status", "responded_at", "updated_at"])
    create_booking_event(
        booking=booking,
        event_type=BookingEvent.EventType.APPLICATION_DECLINED,
        description="Employer declined marketplace application.",
        performed_by=performed_by,
        metadata={"application_id": application.id, "worker_id": application.worker_id},
    )
    return application


@transaction.atomic
def select_application(*, application, performed_by=None):
    booking = application.booking
    _assert_open_marketplace_booking(booking)
    _assert_employer_owner(booking, performed_by)
    _assert_application_open(booking)

    if application.status in [BookingApplication.Status.WITHDRAWN, BookingApplication.Status.DECLINED]:
        raise ValidationError("Cannot select an inactive application.")

    application.status = BookingApplication.Status.SELECTED
    application.responded_at = timezone.now()
    application.save(update_fields=["status", "responded_at", "updated_at"])

    booking.worker = application.worker
    booking.status = Booking.Status.PENDING_WORKER_RESPONSE
    booking.save(update_fields=["worker", "status", "updated_at"])

    booking.applications.exclude(id=application.id).filter(
        status__in=[BookingApplication.Status.PENDING, BookingApplication.Status.SHORTLISTED]
    ).update(status=BookingApplication.Status.DECLINED, responded_at=timezone.now(), updated_at=timezone.now())

    create_booking_event(
        booking=booking,
        event_type=BookingEvent.EventType.EMPLOYER_SELECTED_APPLICANT,
        from_status=Booking.Status.APPLICATIONS_RECEIVED,
        to_status=Booking.Status.PENDING_WORKER_RESPONSE,
        description="Employer selected a worker from marketplace applications.",
        performed_by=performed_by,
        metadata={"application_id": application.id, "worker_id": application.worker_id},
    )
    return booking
