from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from bookings.models import Booking, BookingEvent
from bookings.services.booking_event_service import create_booking_event
from bookings.services.pricing_service import estimate_booking_price


def _validate_booking_request_inputs(
    *,
    employer_profile,
    worker_profile,
    request_type,
    service_category,
    employer_location,
    scheduled_date,
    duration_hours,
):
    if not employer_profile or not employer_profile.is_active:
        raise ValidationError("Employer profile is not active for booking requests.")
    if request_type == Booking.RequestType.DIRECT_REQUEST:
        if not worker_profile or not worker_profile.is_active:
            raise ValidationError("Worker profile is not active for booking requests.")
    elif worker_profile and not worker_profile.is_active:
        raise ValidationError("Worker profile is not active for booking requests.")
    if not service_category or not service_category.is_active:
        raise ValidationError("Selected service category is not active.")
    if employer_location and employer_location.employer_id != employer_profile.id:
        raise ValidationError("Selected location does not belong to this employer profile.")
    if scheduled_date < timezone.localdate():
        raise ValidationError("Scheduled date cannot be in the past.")
    if duration_hours <= 0:
        raise ValidationError("Duration must be greater than zero.")

    if worker_profile and worker_profile.skills.exists() and not worker_profile.skills.filter(category=service_category).exists():
        raise ValidationError("Selected worker does not currently list this service category.")


@transaction.atomic
def create_booking_request(
    *,
    employer_profile,
    service_category,
    employer_location,
    scheduled_date,
    start_time,
    duration_hours,
    special_instructions,
    created_by,
    worker_profile=None,
    request_type=Booking.RequestType.DIRECT_REQUEST,
):
    _validate_booking_request_inputs(
        employer_profile=employer_profile,
        worker_profile=worker_profile,
        request_type=request_type,
        service_category=service_category,
        employer_location=employer_location,
        scheduled_date=scheduled_date,
        duration_hours=duration_hours,
    )

    estimate = estimate_booking_price(service_category, duration_hours)
    booking = Booking.objects.create(
        employer=employer_profile,
        worker=worker_profile,
        request_type=request_type,
        service_category=service_category,
        employer_location=employer_location,
        status=(
            Booking.Status.PENDING_WORKER_RESPONSE
            if request_type == Booking.RequestType.DIRECT_REQUEST
            else Booking.Status.OPEN_FOR_APPLICATIONS
        ),
        scheduled_date=scheduled_date,
        start_time=start_time,
        duration_hours=duration_hours,
        special_instructions=special_instructions.strip(),
        worker_fee_estimate=estimate["worker_fee_estimate"],
        platform_fee_estimate=estimate["platform_fee_estimate"],
        total_estimate=estimate["total_estimate"],
        created_by=created_by,
    )

    create_booking_event(
        booking=booking,
        event_type=(
            BookingEvent.EventType.REQUEST_CREATED
            if request_type == Booking.RequestType.DIRECT_REQUEST
            else BookingEvent.EventType.MARKETPLACE_JOB_POSTED
        ),
        from_status="",
        to_status=booking.status,
        description=(
            "Employer created direct booking request."
            if request_type == Booking.RequestType.DIRECT_REQUEST
            else "Employer posted open marketplace booking."
        ),
        performed_by=created_by,
        metadata={
            "request_type": request_type,
            "scheduled_date": str(scheduled_date),
            "start_time": start_time.isoformat(),
            "duration_hours": duration_hours,
        },
    )
    return booking
