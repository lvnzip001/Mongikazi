from django.contrib import admin

from .models import EmployerLocation, EmployerProfile, EmployerServicePreference, EmployerTrustSignal


class EmployerLocationInline(admin.TabularInline):
    model = EmployerLocation
    extra = 0


class EmployerServicePreferenceInline(admin.TabularInline):
    model = EmployerServicePreference
    extra = 0


class EmployerTrustSignalInline(admin.TabularInline):
    model = EmployerTrustSignal
    extra = 0


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "user",
        "primary_area",
        "employer_type",
        "is_active",
        "is_verified",
        "trust_status",
        "profile_completion_percent",
        "updated_at",
    )
    list_filter = ("is_active", "is_verified", "trust_status", "employer_type", "is_profile_complete")
    search_fields = ("display_name", "user__email", "user__phone_number", "primary_area", "employer_type")
    readonly_fields = ("created_at", "updated_at")
    inlines = (EmployerLocationInline, EmployerServicePreferenceInline, EmployerTrustSignalInline)


@admin.register(EmployerLocation)
class EmployerLocationAdmin(admin.ModelAdmin):
    list_display = ("employer", "label", "suburb", "city", "province", "is_primary", "is_active")
    list_filter = ("is_primary", "is_active", "province")
    search_fields = (
        "employer__display_name",
        "employer__user__email",
        "address_line_1",
        "suburb",
        "city",
        "province",
        "postal_code",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmployerServicePreference)
class EmployerServicePreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "employer",
        "service_type",
        "service_frequency",
        "preferred_day",
        "preferred_time",
        "estimated_duration_hours",
        "updated_at",
    )
    list_filter = ("service_type", "service_frequency", "preferred_day")
    search_fields = ("employer__display_name", "employer__user__email", "special_instructions")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmployerTrustSignal)
class EmployerTrustSignalAdmin(admin.ModelAdmin):
    list_display = ("employer", "signal_type", "status", "updated_at")
    list_filter = ("signal_type", "status")
    search_fields = ("employer__display_name", "employer__user__email", "notes")
    readonly_fields = ("created_at", "updated_at")