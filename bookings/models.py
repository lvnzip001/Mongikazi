from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    class RequestType(models.TextChoices):
        DIRECT_REQUEST = "DIRECT_REQUEST", "Direct request"
        OPEN_MARKETPLACE = "OPEN_MARKETPLACE", "Open marketplace"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        OPEN_FOR_APPLICATIONS = "OPEN_FOR_APPLICATIONS", "Open for applications"
        APPLICATIONS_RECEIVED = "APPLICATIONS_RECEIVED", "Applications received"
        WORKER_SELECTED = "WORKER_SELECTED", "Worker selected"
        PENDING_WORKER_RESPONSE = "PENDING_WORKER_RESPONSE", "Pending worker response"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"
        CANCELLED_BY_EMPLOYER = "CANCELLED_BY_EMPLOYER", "Cancelled by employer"
        CANCELLED_BY_WORKER = "CANCELLED_BY_WORKER", "Cancelled by worker"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        DISPUTED = "DISPUTED", "Disputed"
        CLOSED = "CLOSED", "Closed"

    booking_reference = models.CharField(max_length=32, unique=True, blank=True)
    employer = models.ForeignKey("employers.EmployerProfile", on_delete=models.PROTECT, related_name="bookings")
    worker = models.ForeignKey(
        "helpers.HelperProfile",
        on_delete=models.PROTECT,
        related_name="bookings",
        null=True,
        blank=True,
    )
    request_type = models.CharField(max_length=32, choices=RequestType.choices, default=RequestType.DIRECT_REQUEST)
    service_category = models.ForeignKey("helpers.ServiceCategory", on_delete=models.PROTECT, related_name="bookings")
    employer_location = models.ForeignKey(
        "employers.EmployerLocation",
        on_delete=models.PROTECT,
        related_name="bookings",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING_WORKER_RESPONSE)
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    special_instructions = models.TextField(blank=True)
    worker_fee_estimate = models.DecimalField(max_digits=9, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    platform_fee_estimate = models.DecimalField(max_digits=9, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_estimate = models.DecimalField(max_digits=9, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    decline_reason = models.CharField(max_length=255, blank=True)
    cancel_reason = models.CharField(max_length=255, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_bookings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["booking_reference"]),
            models.Index(fields=["status", "scheduled_date"]),
            models.Index(fields=["employer", "status"]),
            models.Index(fields=["worker", "status"]),
        ]

    def __str__(self):
        return self.booking_reference or f"Booking {self.pk}"

    def clean(self):
        if self.request_type == self.RequestType.DIRECT_REQUEST and not self.worker:
            raise ValidationError({"worker": "Direct request bookings must have an assigned worker."})

        if self.status in [self.Status.ACCEPTED, self.Status.COMPLETED] and not self.worker:
            raise ValidationError({"worker": "Accepted or completed bookings must have an assigned worker."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if not self.booking_reference and self.pk:
            self.booking_reference = f"MK-{self.pk:06d}"
            super().save(update_fields=["booking_reference", "updated_at"])


class BookingEvent(models.Model):
    class EventType(models.TextChoices):
        REQUEST_CREATED = "REQUEST_CREATED", "Request created"
        WORKER_ACCEPTED = "WORKER_ACCEPTED", "Worker accepted"
        WORKER_DECLINED = "WORKER_DECLINED", "Worker declined"
        EMPLOYER_CANCELLED = "EMPLOYER_CANCELLED", "Employer cancelled"
        WORKER_CANCELLED = "WORKER_CANCELLED", "Worker cancelled"
        MARKED_COMPLETED = "MARKED_COMPLETED", "Marked completed"
        MARKETPLACE_JOB_POSTED = "MARKETPLACE_JOB_POSTED", "Marketplace job posted"
        WORKER_APPLIED = "WORKER_APPLIED", "Worker applied"
        WORKER_WITHDREW_APPLICATION = "WORKER_WITHDREW_APPLICATION", "Worker withdrew application"
        EMPLOYER_SELECTED_APPLICANT = "EMPLOYER_SELECTED_APPLICANT", "Employer selected applicant"
        APPLICATION_DECLINED = "APPLICATION_DECLINED", "Application declined"
        STATUS_CHANGED = "STATUS_CHANGED", "Status changed"
        NOTE_ADDED = "NOTE_ADDED", "Note added"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    from_status = models.CharField(max_length=32, blank=True)
    to_status = models.CharField(max_length=32, blank=True)
    description = models.CharField(max_length=255, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_events_performed",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["booking", "created_at"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self):
        return f"{self.booking} - {self.event_type}"


class BookingApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        SELECTED = "SELECTED", "Selected"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"
        DECLINED = "DECLINED", "Declined"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="applications")
    worker = models.ForeignKey("helpers.HelperProfile", on_delete=models.PROTECT, related_name="booking_applications")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True)
    proposed_fee = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["booking", "worker"], name="unique_booking_application_per_worker"),
        ]
        indexes = [
            models.Index(fields=["booking", "status"]),
            models.Index(fields=["worker", "status"]),
        ]

    def clean(self):
        if self.booking and self.booking.request_type != Booking.RequestType.OPEN_MARKETPLACE:
            raise ValidationError({"booking": "Applications can only be created for open marketplace bookings."})

    def __str__(self):
        return f"{self.booking} application by {self.worker}"
