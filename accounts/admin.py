from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


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
