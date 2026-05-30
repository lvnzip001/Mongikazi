from bookings.models import Booking, BookingApplication

WORKER = "worker"
EMPLOYER = "employer"

BOOKING_STATUS_LABELS = {
    Booking.Status.DRAFT: {
        WORKER: ("Draft", "neutral"),
        EMPLOYER: ("Draft", "neutral"),
    },
    Booking.Status.OPEN_FOR_APPLICATIONS: {
        WORKER: ("Open for applications", "neutral"),
        EMPLOYER: ("Open for applications", "neutral"),
    },
    Booking.Status.APPLICATIONS_RECEIVED: {
        WORKER: ("Applications received", "neutral"),
        EMPLOYER: ("Applications received", "warning"),
    },
    Booking.Status.WORKER_SELECTED: {
        WORKER: ("Selected — respond now", "warning"),
        EMPLOYER: ("Worker selected", "warning"),
    },
    Booking.Status.PENDING_WORKER_RESPONSE: {
        WORKER: ("New offer", "pending"),
        EMPLOYER: ("Awaiting worker response", "pending"),
    },
    Booking.Status.ACCEPTED: {
        WORKER: ("Upcoming job", "accepted"),
        EMPLOYER: ("Booking confirmed", "accepted"),
    },
    Booking.Status.DECLINED: {
        WORKER: ("Declined", "declined"),
        EMPLOYER: ("Declined", "declined"),
    },
    Booking.Status.CANCELLED_BY_EMPLOYER: {
        WORKER: ("Cancelled by employer", "cancelled"),
        EMPLOYER: ("Cancelled", "cancelled"),
    },
    Booking.Status.CANCELLED_BY_WORKER: {
        WORKER: ("Cancelled", "cancelled"),
        EMPLOYER: ("Cancelled by worker", "cancelled"),
    },
    Booking.Status.IN_PROGRESS: {
        WORKER: ("In progress", "accepted"),
        EMPLOYER: ("In progress", "accepted"),
    },
    Booking.Status.COMPLETED: {
        WORKER: ("Completed", "completed"),
        EMPLOYER: ("Completed", "completed"),
    },
    Booking.Status.DISPUTED: {
        WORKER: ("Disputed", "warning"),
        EMPLOYER: ("Disputed", "warning"),
    },
    Booking.Status.CLOSED: {
        WORKER: ("Closed", "neutral"),
        EMPLOYER: ("Closed", "neutral"),
    },
}

APPLICATION_STATUS_LABELS = {
    BookingApplication.Status.PENDING: {
        WORKER: ("Applied", "neutral"),
        EMPLOYER: ("Submitted", "neutral"),
    },
    BookingApplication.Status.SHORTLISTED: {
        WORKER: ("Under review", "warning"),
        EMPLOYER: ("Shortlisted", "warning"),
    },
    BookingApplication.Status.SELECTED: {
        WORKER: ("Selected — respond now", "pending"),
        EMPLOYER: ("Worker selected", "warning"),
    },
    BookingApplication.Status.WITHDRAWN: {
        WORKER: ("Withdrawn", "neutral"),
        EMPLOYER: ("Withdrawn", "neutral"),
    },
    BookingApplication.Status.DECLINED: {
        WORKER: ("Declined", "declined"),
        EMPLOYER: ("Declined", "declined"),
    },
}


def get_booking_status_display(status, audience=WORKER):
    mapping = BOOKING_STATUS_LABELS.get(status)
    if not mapping:
        return status.replace("_", " ").title(), "neutral"
    label, variant = mapping.get(audience, mapping.get(WORKER, (status, "neutral")))
    return label, variant


def get_application_status_display(status, audience=WORKER):
    mapping = APPLICATION_STATUS_LABELS.get(status)
    if not mapping:
        return status.replace("_", " ").title(), "neutral"
    label, variant = mapping.get(audience, mapping.get(WORKER, (status, "neutral")))
    return label, variant
