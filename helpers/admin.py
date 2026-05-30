from django.contrib import admin, messages

from helpers.models import (
    HelperAvailability,
    HelperProfile,
    HelperSkill,
    HelperTrustSignal,
    ServiceCategory,
    WorkerVerificationDocument,
)
from helpers.services.verification_service import review_worker_verification_document, sync_verification_trust_signals


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


@admin.register(WorkerVerificationDocument)
class WorkerVerificationDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "helper",
        "document_type",
        "status",
        "is_current",
        "uploaded_at",
        "reviewed_at",
        "reviewed_by",
    )
    list_filter = ("document_type", "status", "is_current")
    search_fields = ("helper__display_name", "helper__user__email", "review_note")
    readonly_fields = ("uploaded_at", "created_at", "updated_at")
    actions = ("approve_documents", "reject_documents", "mark_pending_review")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_current:
            sync_verification_trust_signals(obj.helper)

    @admin.action(description="Approve selected documents")
    def approve_documents(self, request, queryset):
        updated = 0
        for document in queryset.filter(is_current=True):
            review_worker_verification_document(
                document=document,
                reviewer=request.user,
                status=WorkerVerificationDocument.Status.APPROVED,
            )
            updated += 1
        self.message_user(request, f"Approved {updated} document(s).", messages.SUCCESS)

    @admin.action(description="Reject selected documents")
    def reject_documents(self, request, queryset):
        updated = 0
        for document in queryset.filter(is_current=True):
            review_worker_verification_document(
                document=document,
                reviewer=request.user,
                status=WorkerVerificationDocument.Status.REJECTED,
                review_note="Please upload a clearer or updated document.",
            )
            updated += 1
        self.message_user(request, f"Rejected {updated} document(s).", messages.WARNING)

    @admin.action(description="Mark selected as pending review")
    def mark_pending_review(self, request, queryset):
        updated = 0
        for document in queryset.filter(is_current=True):
            review_worker_verification_document(
                document=document,
                reviewer=request.user,
                status=WorkerVerificationDocument.Status.PENDING_REVIEW,
            )
            updated += 1
        self.message_user(request, f"Marked {updated} document(s) as pending review.", messages.INFO)
