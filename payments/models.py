from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Invoice(models.Model):
    class Status(models.TextChoices):
        ISSUED = "ISSUED", "Issued"
        PROOF_SUBMITTED = "PROOF_SUBMITTED", "Proof submitted"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    class PayoutStatus(models.TextChoices):
        NOT_READY = "NOT_READY", "Not ready"
        READY_FOR_PAYOUT = "READY_FOR_PAYOUT", "Ready for payout"
        PAID_OUT = "PAID_OUT", "Paid out"

    booking = models.OneToOneField("bookings.Booking", on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=32, unique=True, blank=True)
    employer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employer_invoices",
    )
    helper_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="helper_invoices",
    )
    worker_fee_amount = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0)])
    platform_fee_amount = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.ISSUED)
    payout_status = models.CharField(max_length=24, choices=PayoutStatus.choices, default=PayoutStatus.NOT_READY)
    paid_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_payouts_marked",
    )
    payout_reference = models.CharField(max_length=80, blank=True)
    issued_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_out_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_at", "-id"]
        indexes = [
            models.Index(fields=["employer_user", "status"]),
            models.Index(fields=["helper_user", "status"]),
            models.Index(fields=["invoice_number"]),
        ]

    def clean(self):
        if not self.booking_id:
            return

        if self.booking.status != self.booking.Status.COMPLETED and self.status != self.Status.CANCELLED:
            raise ValidationError({"booking": "Invoices can only be issued for completed bookings."})

        if self.booking.employer.user_id != self.employer_user_id:
            raise ValidationError({"employer_user": "Employer does not match booking employer."})

        if not self.booking.worker_id or self.booking.worker.user_id != self.helper_user_id:
            raise ValidationError({"helper_user": "Helper does not match booking worker."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if not self.invoice_number and self.pk:
            self.invoice_number = f"INV-{self.pk:06d}"
            super().save(update_fields=["invoice_number", "updated_at"])

    def __str__(self):
        return self.invoice_number or f"Invoice {self.pk}"


class Payment(models.Model):
    class Method(models.TextChoices):
        EFT = "EFT", "EFT"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank transfer"
        CASH = "CASH", "Cash"

    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_payments")
    method = models.CharField(max_length=20, choices=Method.choices)
    amount = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0)])
    payer_reference = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_payments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at", "-id"]
        indexes = [
            models.Index(fields=["invoice", "status"]),
            models.Index(fields=["submitted_by", "status"]),
        ]

    def clean(self):
        if self.submitted_by_id != self.invoice.employer_user_id:
            raise ValidationError({"submitted_by": "Only booking employer can submit payment proof."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id} for {self.invoice}"


class PaymentProof(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="proofs")
    note = models.TextField(blank=True)
    document_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Proof {self.id} for payment {self.payment_id}"


class PayoutAuditLog(models.Model):
    class Action(models.TextChoices):
        MARKED_PAID_OUT = "MARKED_PAID_OUT", "Marked paid out"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payout_audit_logs")
    action = models.CharField(max_length=24, choices=Action.choices)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payout_audit_actions",
    )
    payout_reference = models.CharField(max_length=80, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["invoice", "created_at"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.action}"




