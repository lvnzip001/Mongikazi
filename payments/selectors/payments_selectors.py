from django.db.models import Sum

from payments.models import Invoice, Payment, PayoutAuditLog


def get_employer_invoices(user):
    return Invoice.objects.select_related("booking", "helper_user").filter(employer_user=user)


def get_helper_invoices(user):
    return Invoice.objects.select_related("booking", "employer_user").filter(helper_user=user)


def get_invoice_for_employer(user, invoice_id):
    return Invoice.objects.select_related("booking", "helper_user").filter(id=invoice_id, employer_user=user).first()


def get_invoice_for_helper(user, invoice_id):
    return Invoice.objects.select_related("booking", "employer_user").filter(id=invoice_id, helper_user=user).first()


def get_helper_earnings_summary(user):
    invoices = get_helper_invoices(user)
    employer_paid_total = invoices.filter(status=Invoice.Status.PAID).aggregate(total=Sum("worker_fee_amount")).get("total") or 0
    paid_out_total = (
        invoices.filter(payout_status=Invoice.PayoutStatus.PAID_OUT).aggregate(total=Sum("worker_fee_amount")).get("total")
        or 0
    )
    proof_submitted_total = (
        invoices.filter(status=Invoice.Status.PROOF_SUBMITTED).aggregate(total=Sum("worker_fee_amount")).get("total") or 0
    )
    issued_total = invoices.filter(status=Invoice.Status.ISSUED).aggregate(total=Sum("worker_fee_amount")).get("total") or 0
    pending_total = proof_submitted_total + issued_total
    return {
        "employer_paid_total": employer_paid_total,
        "paid_out_total": paid_out_total,
        "paid_total": paid_out_total,
        "proof_submitted_total": proof_submitted_total,
        "issued_total": issued_total,
        "pending_total": pending_total,
        "invoice_count": invoices.count(),
    }


def get_submitted_payments_for_operations():
    return Payment.objects.select_related(
        "invoice",
        "invoice__booking",
        "invoice__employer_user",
        "invoice__helper_user",
    ).filter(status=Payment.Status.SUBMITTED)


def get_payment_for_operations(payment_id):
    return (
        Payment.objects.select_related("invoice", "invoice__booking", "invoice__employer_user", "invoice__helper_user")
        .filter(id=payment_id)
        .first()
    )


def get_invoices_ready_for_payout():
    return Invoice.objects.select_related("booking", "employer_user", "helper_user").filter(
        status=Invoice.Status.PAID,
        payout_status=Invoice.PayoutStatus.READY_FOR_PAYOUT,
    )


def get_invoice_for_operations(invoice_id):
    return Invoice.objects.select_related("booking", "employer_user", "helper_user").filter(id=invoice_id).first()


def get_payout_audit_logs():
    return PayoutAuditLog.objects.select_related(
        "invoice",
        "invoice__booking",
        "invoice__employer_user",
        "invoice__helper_user",
        "performed_by",
    )



