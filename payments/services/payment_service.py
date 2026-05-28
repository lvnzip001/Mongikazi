from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from bookings.models import Booking
from payments.models import Invoice, Payment, PaymentProof, PayoutAuditLog


@transaction.atomic
def issue_invoice_for_completed_booking(booking):
    if booking.status != Booking.Status.COMPLETED:
        raise ValidationError("Invoice can only be issued for completed bookings.")
    if not booking.worker_id:
        raise ValidationError("Cannot issue invoice for booking without assigned worker.")

    due_at = timezone.now() + timedelta(days=3)
    invoice, created = Invoice.objects.get_or_create(
        booking=booking,
        defaults={
            "employer_user": booking.employer.user,
            "helper_user": booking.worker.user,
            "worker_fee_amount": booking.worker_fee_estimate,
            "platform_fee_amount": booking.platform_fee_estimate,
            "total_amount": booking.total_estimate,
            "status": Invoice.Status.ISSUED,
            "payout_status": Invoice.PayoutStatus.NOT_READY,
            "issued_at": timezone.now(),
            "due_at": due_at,
        },
    )

    if not created:
        invoice.employer_user = booking.employer.user
        invoice.helper_user = booking.worker.user
        invoice.worker_fee_amount = booking.worker_fee_estimate
        invoice.platform_fee_amount = booking.platform_fee_estimate
        invoice.total_amount = booking.total_estimate
        if invoice.status == Invoice.Status.CANCELLED:
            invoice.status = Invoice.Status.ISSUED
        if invoice.payout_status != Invoice.PayoutStatus.PAID_OUT:
            invoice.payout_status = Invoice.PayoutStatus.NOT_READY
            invoice.paid_out_at = None
        if not invoice.due_at:
            invoice.due_at = due_at
        invoice.save(
            update_fields=[
                "employer_user",
                "helper_user",
                "worker_fee_amount",
                "platform_fee_amount",
                "total_amount",
                "status",
                "payout_status",
                "due_at",
                "paid_out_at",
                "updated_at",
            ]
        )

    return invoice


@transaction.atomic
def submit_payment_proof(*, invoice, employer_user, method, amount, payer_reference="", note="", document_url=""):
    if invoice.employer_user_id != employer_user.id:
        raise ValidationError("Only the invoice employer can submit payment proof.")
    if invoice.status == Invoice.Status.CANCELLED:
        raise ValidationError("Cannot submit proof for a cancelled invoice.")

    payment = Payment.objects.create(
        invoice=invoice,
        submitted_by=employer_user,
        method=method,
        amount=amount,
        payer_reference=(payer_reference or "").strip(),
        status=Payment.Status.SUBMITTED,
    )
    PaymentProof.objects.create(
        payment=payment,
        note=(note or "").strip(),
        document_url=(document_url or "").strip(),
    )

    if invoice.status == Invoice.Status.ISSUED:
        invoice.status = Invoice.Status.PROOF_SUBMITTED
        invoice.save(update_fields=["status", "updated_at"])

    return payment


def _assert_operations_actor(actor):
    if not actor or not getattr(actor, "is_operations_user", False):
        raise ValidationError("Only operations users can review payment submissions.")


def _refresh_invoice_status_from_payments(invoice):
    verified_total = (
        invoice.payments.filter(status=Payment.Status.VERIFIED).aggregate(total=Sum("amount")).get("total") or 0
    )
    has_submitted = invoice.payments.filter(status=Payment.Status.SUBMITTED).exists()

    if verified_total >= invoice.total_amount:
        invoice.status = Invoice.Status.PAID
        if not invoice.paid_at:
            invoice.paid_at = timezone.now()
        if invoice.payout_status != Invoice.PayoutStatus.PAID_OUT:
            invoice.payout_status = Invoice.PayoutStatus.READY_FOR_PAYOUT
    elif has_submitted:
        invoice.status = Invoice.Status.PROOF_SUBMITTED
        invoice.paid_at = None
        if invoice.payout_status != Invoice.PayoutStatus.PAID_OUT:
            invoice.payout_status = Invoice.PayoutStatus.NOT_READY
            invoice.paid_out_at = None
    else:
        invoice.status = Invoice.Status.ISSUED
        invoice.paid_at = None
        if invoice.payout_status != Invoice.PayoutStatus.PAID_OUT:
            invoice.payout_status = Invoice.PayoutStatus.NOT_READY
            invoice.paid_out_at = None
    invoice.save(update_fields=["status", "paid_at", "payout_status", "paid_out_at", "updated_at"])


@transaction.atomic
def verify_payment_submission(*, payment, reviewed_by):
    _assert_operations_actor(reviewed_by)
    if payment.status != Payment.Status.SUBMITTED:
        raise ValidationError("Only submitted payments can be verified.")

    payment.status = Payment.Status.VERIFIED
    payment.reviewed_at = timezone.now()
    payment.reviewed_by = reviewed_by
    payment.save(update_fields=["status", "reviewed_at", "reviewed_by", "updated_at"])
    _refresh_invoice_status_from_payments(payment.invoice)
    return payment


@transaction.atomic
def reject_payment_submission(*, payment, reviewed_by):
    _assert_operations_actor(reviewed_by)
    if payment.status != Payment.Status.SUBMITTED:
        raise ValidationError("Only submitted payments can be rejected.")

    payment.status = Payment.Status.REJECTED
    payment.reviewed_at = timezone.now()
    payment.reviewed_by = reviewed_by
    payment.save(update_fields=["status", "reviewed_at", "reviewed_by", "updated_at"])
    _refresh_invoice_status_from_payments(payment.invoice)
    return payment


@transaction.atomic
def mark_invoice_paid_out(*, invoice, reviewed_by, payout_reference="", note=""):
    _assert_operations_actor(reviewed_by)
    if invoice.status != Invoice.Status.PAID:
        raise ValidationError("Invoice must be paid before payout can be marked complete.")
    if invoice.payout_status == Invoice.PayoutStatus.PAID_OUT:
        return invoice
    if invoice.payout_status != Invoice.PayoutStatus.READY_FOR_PAYOUT:
        raise ValidationError("Invoice is not ready for payout.")

    invoice.payout_status = Invoice.PayoutStatus.PAID_OUT
    invoice.paid_out_at = timezone.now()
    invoice.paid_out_by = reviewed_by
    invoice.payout_reference = (payout_reference or "").strip()
    invoice.save(update_fields=["payout_status", "paid_out_at", "paid_out_by", "payout_reference", "updated_at"])
    PayoutAuditLog.objects.create(
        invoice=invoice,
        action=PayoutAuditLog.Action.MARKED_PAID_OUT,
        performed_by=reviewed_by,
        payout_reference=invoice.payout_reference,
        note=(note or "").strip(),
    )
    return invoice




