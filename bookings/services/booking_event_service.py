from bookings.models import BookingEvent


def create_booking_event(
    *,
    booking,
    event_type,
    from_status="",
    to_status="",
    description="",
    performed_by=None,
    metadata=None,
):
    return BookingEvent.objects.create(
        booking=booking,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        description=description,
        performed_by=performed_by,
        metadata=metadata or {},
    )
