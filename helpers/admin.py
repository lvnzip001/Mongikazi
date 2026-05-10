from django.contrib import admin

from .models import HelperAvailability, HelperProfile, HelperSkill, HelperTrustSignal, ServiceCategory


class HelperSkillInline(admin.TabularInline):
    model = HelperSkill
    extra = 0


class HelperAvailabilityInline(admin.TabularInline):
    model = HelperAvailability
    extra = 0


class HelperTrustSignalInline(admin.TabularInline):
    model = HelperTrustSignal
    extra = 0


@admin.register(HelperProfile)
class HelperProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "user",
        "location",
        "is_active",
        "is_verified",
        "trust_status",
        "profile_completion_percent",
        "updated_at",
    )
    list_filter = ("is_active", "is_verified", "trust_status", "is_profile_complete")
    search_fields = ("display_name", "user__email", "user__phone_number", "location")
    readonly_fields = ("created_at", "updated_at")
    inlines = (HelperSkillInline, HelperAvailabilityInline, HelperTrustSignalInline)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")


@admin.register(HelperSkill)
class HelperSkillAdmin(admin.ModelAdmin):
    list_display = ("helper", "category", "years_experience", "is_primary", "updated_at")
    list_filter = ("is_primary", "category")
    search_fields = ("helper__display_name", "helper__user__email", "category__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(HelperAvailability)
class HelperAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("helper", "day_of_week", "start_time", "end_time", "is_available")
    list_filter = ("day_of_week", "is_available")
    search_fields = ("helper__display_name", "helper__user__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(HelperTrustSignal)
class HelperTrustSignalAdmin(admin.ModelAdmin):
    list_display = ("helper", "signal_type", "status", "updated_at")
    list_filter = ("signal_type", "status")
    search_fields = ("helper__display_name", "helper__user__email", "notes")
    readonly_fields = ("created_at", "updated_at")
