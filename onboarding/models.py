from django.db import models
from django.conf import settings


class EmployerOnboardingProfile(models.Model):
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

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employer_onboarding")
    preferred_location = models.CharField(max_length=255, blank=True)
    preferred_location_locality = models.ForeignKey(
        "locations.Locality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employer_onboarding_locations",
    )
    service_type = models.CharField(max_length=40, choices=ServiceType.choices, blank=True)
    service_frequency = models.CharField(max_length=30, choices=ServiceFrequency.choices, blank=True)
    preferred_start_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    special_instructions = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employer onboarding: {self.user_id}"


class HelperOnboardingProfile(models.Model):
    DEFAULT_AVAILABILITY_SUMMARY = "08:00 to 16:00"

    class ServiceCategory(models.TextChoices):
        CLEANING = "cleaning", "Cleaning"
        LAUNDRY = "laundry", "Laundry"
        COOKING = "cooking", "Cooking"
        CHILDCARE = "childcare", "Childcare"
        OFFICE_CLEANING = "office_cleaning", "Office cleaning"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="helper_onboarding")
    display_name = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=255, blank=True)
    location_locality = models.ForeignKey(
        "locations.Locality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="helper_onboarding_locations",
    )
    years_experience = models.PositiveSmallIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    selected_categories = models.TextField(blank=True)
    has_id_document_ready = models.BooleanField(null=True, blank=True)
    has_criminal_check_ready = models.BooleanField(null=True, blank=True)
    has_references = models.BooleanField(null=True, blank=True)
    preferred_work_area = models.CharField(max_length=255, blank=True)
    preferred_work_area_locality = models.ForeignKey(
        "locations.Locality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="helper_onboarding_work_areas",
    )
    availability_summary = models.CharField(max_length=255, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def categories_list(self):
        return [item for item in self.selected_categories.split(",") if item]

    def __str__(self):
        return f"Helper onboarding: {self.user_id}"
