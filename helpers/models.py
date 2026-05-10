from django.conf import settings
from django.db import models
from django.utils.text import slugify


class HelperProfile(models.Model):
    class TrustStatus(models.TextChoices):
        NEW = "NEW", "New"
        PROFILE_STARTED = "PROFILE_STARTED", "Profile started"
        READY_FOR_REVIEW = "READY_FOR_REVIEW", "Ready for review"
        VERIFIED = "VERIFIED", "Verified"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="helper_profile")
    display_name = models.CharField(max_length=120, blank=True)
    profile_photo = models.FileField(upload_to="helpers/profile_photos/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    preferred_work_area = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    availability_summary = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_profile_complete = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    trust_status = models.CharField(max_length=24, choices=TrustStatus.choices, default=TrustStatus.NEW)
    profile_completion_percent = models.PositiveSmallIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    completed_jobs = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "is_profile_complete"]),
            models.Index(fields=["trust_status"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return self.display_name or f"Helper {self.user_id}"


class ServiceCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HelperSkill(models.Model):
    helper = models.ForeignKey(HelperProfile, on_delete=models.CASCADE, related_name="skills")
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="helper_skills")
    years_experience = models.PositiveSmallIntegerField(default=0)
    skill_note = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("helper", "category")
        ordering = ["-is_primary", "category__sort_order", "category__name"]

    def __str__(self):
        return f"{self.helper} - {self.category}"


class HelperAvailability(models.Model):
    class DayOfWeek(models.TextChoices):
        MONDAY = "MONDAY", "Monday"
        TUESDAY = "TUESDAY", "Tuesday"
        WEDNESDAY = "WEDNESDAY", "Wednesday"
        THURSDAY = "THURSDAY", "Thursday"
        FRIDAY = "FRIDAY", "Friday"
        SATURDAY = "SATURDAY", "Saturday"
        SUNDAY = "SUNDAY", "Sunday"

    helper = models.ForeignKey(HelperProfile, on_delete=models.CASCADE, related_name="availability")
    day_of_week = models.CharField(max_length=10, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("helper", "day_of_week", "start_time", "end_time")
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.helper} {self.day_of_week} {self.start_time}-{self.end_time}"


class HelperTrustSignal(models.Model):
    class SignalType(models.TextChoices):
        ID_DOCUMENT = "ID_DOCUMENT", "ID document"
        CRIMINAL_RECORD_CHECK = "CRIMINAL_RECORD_CHECK", "Criminal record check"
        REFERENCES = "REFERENCES", "References"
        EXPERIENCE_CAPTURED = "EXPERIENCE_CAPTURED", "Experience captured"
        PROFILE_PHOTO = "PROFILE_PHOTO", "Profile photo"

    class SignalStatus(models.TextChoices):
        NOT_PROVIDED = "NOT_PROVIDED", "Not provided"
        READY = "READY", "Ready"
        PENDING_REVIEW = "PENDING_REVIEW", "Pending review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    helper = models.ForeignKey(HelperProfile, on_delete=models.CASCADE, related_name="trust_signals")
    signal_type = models.CharField(max_length=40, choices=SignalType.choices)
    status = models.CharField(max_length=20, choices=SignalStatus.choices, default=SignalStatus.NOT_PROVIDED)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("helper", "signal_type")
        ordering = ["signal_type"]

    def __str__(self):
        return f"{self.helper} - {self.signal_type}"
