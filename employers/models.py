from django.conf import settings
from django.db import models


class EmployerProfile(models.Model):
    class EmployerType(models.TextChoices):
        HOUSEHOLD = "HOUSEHOLD", "Household"
        BUSINESS = "BUSINESS", "Business"
        PROPERTY = "PROPERTY", "Property / landlord"
        OTHER = "OTHER", "Other"

    class ContactMethod(models.TextChoices):
        APP = "APP", "App"
        PHONE = "PHONE", "Phone"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        EMAIL = "EMAIL", "Email"

    class TrustStatus(models.TextChoices):
        NEW = "NEW", "New"
        PROFILE_STARTED = "PROFILE_STARTED", "Profile started"
        READY_FOR_BOOKING = "READY_FOR_BOOKING", "Ready for booking"
        VERIFIED = "VERIFIED", "Verified"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employer_profile")
    display_name = models.CharField(max_length=120, blank=True)
    profile_photo = models.ImageField(upload_to="employers/profile_photos/%Y/%m/", blank=True, null=True)
    employer_type = models.CharField(max_length=20, choices=EmployerType.choices, default=EmployerType.HOUSEHOLD)
    primary_location_label = models.CharField(max_length=80, blank=True)
    primary_area = models.CharField(max_length=255, blank=True)
    primary_area_locality = models.ForeignKey(
        "locations.Locality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employer_profiles",
    )
    contact_number = models.CharField(max_length=20, blank=True)
    preferred_contact_method = models.CharField(max_length=20, choices=ContactMethod.choices, blank=True)
    is_active = models.BooleanField(default=True)
    is_profile_complete = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    trust_status = models.CharField(max_length=24, choices=TrustStatus.choices, default=TrustStatus.NEW)
    profile_completion_percent = models.PositiveSmallIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "is_profile_complete"]),
            models.Index(fields=["trust_status"]),
            models.Index(fields=["primary_area"]),
            models.Index(fields=["employer_type"]),
        ]

    def __str__(self):
        return self.display_name or f"Employer {self.user_id}"


class EmployerLocation(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="locations")
    label = models.CharField(max_length=80, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    suburb = models.CharField(max_length=120, blank=True)
    locality = models.ForeignKey(
        "locations.Locality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employer_locations",
    )
    city = models.CharField(max_length=120, blank=True)
    province = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    notes_for_helper = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_primary", "-updated_at"]

    def __str__(self):
        if self.label:
            return f"{self.employer} - {self.label}"
        return f"{self.employer} location"

    def service_area_display(self):
        """Human-readable area for workers (suburb/city), without full street address."""
        parts = []
        if self.locality_id:
            parts.append(self.locality.name)
        if self.suburb and self.suburb not in parts:
            parts.append(self.suburb)
        if self.city and self.city not in parts:
            parts.append(self.city)
        if self.province and self.province not in parts:
            parts.append(self.province)
        area = ", ".join(parts)
        if self.label and area:
            return f"{self.label} · {area}"
        return self.label or area or "Location on file"


class EmployerServicePreference(models.Model):
    class ServiceType(models.TextChoices):
        ONCE_OFF_CLEANING = "once_off_cleaning", "Once-off cleaning"
        RECURRING_HELP = "recurring_help", "Recurring help"
        OFFICE_CLEANING = "office_cleaning", "Office cleaning"
        LAUNDRY = "laundry", "Laundry"
        COOKING = "cooking", "Cooking"
        CHILDCARE = "childcare", "Childcare"

    class ServiceFrequency(models.TextChoices):
        ONCE_OFF = "once_off", "Once-off"
        WEEKLY = "weekly", "Weekly"
        BI_WEEKLY = "bi_weekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        AS_NEEDED = "as_needed", "As needed"

    class PreferredDay(models.TextChoices):
        MONDAY = "MONDAY", "Monday"
        TUESDAY = "TUESDAY", "Tuesday"
        WEDNESDAY = "WEDNESDAY", "Wednesday"
        THURSDAY = "THURSDAY", "Thursday"
        FRIDAY = "FRIDAY", "Friday"
        SATURDAY = "SATURDAY", "Saturday"
        SUNDAY = "SUNDAY", "Sunday"
        FLEXIBLE = "FLEXIBLE", "Flexible"

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="service_preferences")
    service_type = models.CharField(max_length=40, choices=ServiceType.choices, blank=True)
    service_frequency = models.CharField(max_length=30, choices=ServiceFrequency.choices, blank=True)
    preferred_day = models.CharField(max_length=10, choices=PreferredDay.choices, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    estimated_duration_hours = models.PositiveSmallIntegerField(default=4)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        if self.service_type:
            return f"{self.employer} - {self.get_service_type_display()}"
        return f"{self.employer} preferences"


class EmployerTrustSignal(models.Model):
    class SignalType(models.TextChoices):
        PHONE_VERIFIED = "PHONE_VERIFIED", "Phone verified"
        LOCATION_CAPTURED = "LOCATION_CAPTURED", "Location captured"
        SERVICE_NEED_CAPTURED = "SERVICE_NEED_CAPTURED", "Service need captured"
        BOOKING_HISTORY = "BOOKING_HISTORY", "Booking history"
        PAYMENT_READINESS = "PAYMENT_READINESS", "Payment readiness"

    class SignalStatus(models.TextChoices):
        NOT_PROVIDED = "NOT_PROVIDED", "Not provided"
        READY = "READY", "Ready"
        PENDING_REVIEW = "PENDING_REVIEW", "Pending review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="trust_signals")
    signal_type = models.CharField(max_length=40, choices=SignalType.choices)
    status = models.CharField(max_length=20, choices=SignalStatus.choices, default=SignalStatus.NOT_PROVIDED)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("employer", "signal_type")
        ordering = ["signal_type"]

    def __str__(self):
        return f"{self.employer} - {self.signal_type}"