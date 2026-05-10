from django.contrib import admin

from .models import EmployerOnboardingProfile, HelperOnboardingProfile


@admin.register(EmployerOnboardingProfile)
class EmployerOnboardingProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "service_type", "service_frequency", "preferred_location", "is_completed", "updated_at")
    list_filter = ("service_type", "service_frequency", "is_completed")
    search_fields = ("user__username", "user__email", "preferred_location")


@admin.register(HelperOnboardingProfile)
class HelperOnboardingProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "location", "years_experience", "is_completed", "updated_at")
    list_filter = ("is_completed", "has_id_document_ready", "has_criminal_check_ready", "has_references")
    search_fields = ("user__username", "user__email", "display_name", "location")
