from django.contrib import admin

from payments.models import Invoice, Payment, PaymentProof, PayoutAuditLog
from payments.services.payment_service import reject_payment_submission, verify_payment_submission


class PaymentProofInline(admin.TabularInline):
    model = PaymentProof
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ("method", "amount", "status", "submitted_by", "submitted_at")
    readonly_fields = ("submitted_at",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "booking",
        "status",
        "payout_status",
        "total_amount",
        "issued_at",
        "paid_at",
        "paid_out_at",
    )
    list_filter = ("status", "payout_status")
    search_fields = ("invoice_number", "booking__booking_reference", "employer_user__email", "helper_user__email")
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "method", "amount", "status", "submitted_by", "submitted_at", "reviewed_by", "reviewed_at")
    list_filter = ("status", "method")
    search_fields = ("invoice__invoice_number", "invoice__booking__booking_reference", "submitted_by__email")
    inlines = [PaymentProofInline]
    actions = ["mark_verified", "mark_rejected"]

    @admin.action(description="Mark selected submitted payments as VERIFIED")
    def mark_verified(self, request, queryset):
        updated = 0
        for payment in queryset.filter(status=Payment.Status.SUBMITTED):
            verify_payment_submission(payment=payment, reviewed_by=request.user)
            updated += 1
        self.message_user(request, f"{updated} payment(s) marked verified.")

    @admin.action(description="Mark selected submitted payments as REJECTED")
    def mark_rejected(self, request, queryset):
        updated = 0
        for payment in queryset.filter(status=Payment.Status.SUBMITTED):
            reject_payment_submission(payment=payment, reviewed_by=request.user)
            updated += 1
        self.message_user(request, f"{updated} payment(s) marked rejected.")


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ("id", "payment", "created_at")
    search_fields = ("payment__invoice__invoice_number", "payment__invoice__booking__booking_reference", "note")


@admin.register(PayoutAuditLog)
class PayoutAuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "action", "performed_by", "payout_reference", "created_at")
    list_filter = ("action",)
    search_fields = ("invoice__invoice_number", "invoice__booking__booking_reference", "performed_by__email", "payout_reference", "note")



