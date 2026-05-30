from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserPolicyAcceptance


@admin.register(User)
class MongiKaziUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "phone_number",
        "role",
        "is_phone_verified",
        "is_onboarding_complete",
        "accepted_terms",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "role",
        "is_phone_verified",
        "is_onboarding_complete",
        "accepted_terms",
        "is_staff",
        "is_active",
    )
    search_fields = ("username", "email", "phone_number", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("accepted_terms_at", "last_login", "date_joined")

    fieldsets = UserAdmin.fieldsets + (
        (
            "MongiKazi Profile",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "is_phone_verified",
                    "is_onboarding_complete",
                    "accepted_terms",
                    "accepted_terms_at",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("MongiKazi Profile", {"fields": ("role", "email", "phone_number", "accepted_terms")}),
    )


@admin.register(UserPolicyAcceptance)
class UserPolicyAcceptanceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "source",
        "terms_version",
        "privacy_version",
        "safety_version",
        "ip_address",
        "accepted_at",
    )
    list_filter = ("source", "terms_version", "privacy_version", "safety_version", "accepted_at")
    search_fields = ("user__email", "user__phone_number", "user__username", "ip_address", "user_agent")
    readonly_fields = (
        "user",
        "source",
        "terms_version",
        "privacy_version",
        "safety_version",
        "ip_address",
        "user_agent",
        "accepted_at",
    )
