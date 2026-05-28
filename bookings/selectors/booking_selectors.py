from django.db.models import Q

from bookings.models import Booking, BookingApplication


def _booking_lookup_q(booking_id_or_reference):
    lookup = Q(booking_reference=booking_id_or_reference)
    try:
        lookup = lookup | Q(id=int(booking_id_or_reference))
    except (TypeError, ValueError):
        pass
    return lookup


def get_booking_for_employer(user, booking_id_or_reference):
    return (
        Booking.objects.select_related("employer", "worker", "service_category", "employer_location")
        .filter(employer__user=user)
        .filter(_booking_lookup_q(booking_id_or_reference))
        .first()
    )


def get_booking_for_worker(user, booking_id_or_reference):
    return (
        Booking.objects.select_related("employer", "worker", "service_category", "employer_location")
        .filter(worker__user=user)
        .filter(_booking_lookup_q(booking_id_or_reference))
        .first()
    )


def get_employer_bookings(user):
    return Booking.objects.select_related("worker", "service_category", "employer_location").filter(employer__user=user)


def get_worker_booking_requests(user):
    return (
        Booking.objects.select_related("employer", "service_category", "employer_location")
        .filter(worker__user=user, status=Booking.Status.PENDING_WORKER_RESPONSE)
    )


def get_worker_jobs(user):
    return (
        Booking.objects.select_related("employer", "service_category", "employer_location")
        .filter(
            worker__user=user,
            status__in=[
                Booking.Status.ACCEPTED,
                Booking.Status.IN_PROGRESS,
                Booking.Status.COMPLETED,
                Booking.Status.CANCELLED_BY_WORKER,
            ],
        )
    )


def get_worker_open_marketplace_jobs(user):
    return (
        Booking.objects.select_related("employer", "service_category", "employer_location")
        .filter(request_type=Booking.RequestType.OPEN_MARKETPLACE, worker__isnull=True)
        .filter(status__in=[Booking.Status.OPEN_FOR_APPLICATIONS, Booking.Status.APPLICATIONS_RECEIVED])
        .exclude(employer__user=user)
    )


def get_worker_applications(user):
    return BookingApplication.objects.select_related("booking", "booking__employer", "booking__service_category", "worker").filter(
        worker__user=user
    )


def get_employer_marketplace_jobs(user):
    return Booking.objects.select_related("service_category", "employer_location").filter(
        employer__user=user,
        request_type=Booking.RequestType.OPEN_MARKETPLACE,
    )


def get_booking_applications_for_employer(user, booking_reference):
    booking = get_booking_for_employer(user, booking_reference)
    if not booking:
        return None, BookingApplication.objects.none()
    applications = booking.applications.select_related("worker", "worker__user").all()
    return booking, applications


def get_booking_application_for_worker(user, application_id):
    return BookingApplication.objects.select_related("booking", "worker").filter(id=application_id, worker__user=user).first()


def get_booking_application_for_employer(user, application_id):
    return (
        BookingApplication.objects.select_related("booking", "worker")
        .filter(id=application_id, booking__employer__user=user)
        .first()
    )


def get_booking_events(booking):
    return booking.events.select_related("performed_by")


def get_pending_worker_requests(worker_profile):
    return Booking.objects.filter(worker=worker_profile, status=Booking.Status.PENDING_WORKER_RESPONSE)


def get_upcoming_employer_bookings(employer_profile):
    return Booking.objects.filter(
        employer=employer_profile,
        status__in=[Booking.Status.PENDING_WORKER_RESPONSE, Booking.Status.ACCEPTED],
    )


def get_upcoming_worker_jobs(worker_profile):
    return Booking.objects.filter(worker=worker_profile, status__in=[Booking.Status.ACCEPTED, Booking.Status.IN_PROGRESS])


def get_booking_timeline_for_user(user, booking_reference):
    booking = get_booking_for_employer(user, booking_reference) or get_booking_for_worker(user, booking_reference)
    if not booking:
        return None, None
    return booking, get_booking_events(booking)
