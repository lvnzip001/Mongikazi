from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from payments.forms import OperationsPayoutForm, PaymentProofForm
from payments.selectors.payments_selectors import (
    get_employer_invoices,
    get_helper_earnings_summary,
    get_helper_invoices,
    get_invoice_for_employer,
    get_invoice_for_operations,
    get_invoices_ready_for_payout,
    get_payment_for_operations,
    get_payout_audit_logs,
    get_submitted_payments_for_operations,
)
from payments.services.payment_service import (
    mark_invoice_paid_out,
    reject_payment_submission,
    submit_payment_proof,
    verify_payment_submission,
)


def _employer_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_employer", False):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _helper_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_helper", False):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _operations_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_operations_user", False):
        return redirect("onboarding:start")
    return None


@login_required
@require_http_methods(["GET"])
def employer_invoices(request):
    guard = _employer_guard(request)
    if guard:
        return guard

    invoices = get_employer_invoices(request.user)
    return render(
        request,
        "payments/employer_invoices.html",
        {
            "invoices": invoices,
            "portal_kind": "employer",
        },
    )


@login_required
@require_http_methods(["GET"])
def employer_invoice_detail(request, invoice_id):
    guard = _employer_guard(request)
    if guard:
        return guard

    invoice = get_invoice_for_employer(request.user, invoice_id)
    if not invoice:
        raise Http404("Invoice not found")

    return render(
        request,
        "payments/employer_invoice_detail.html",
        {
            "invoice": invoice,
            "proof_form": PaymentProofForm(initial={"amount": invoice.total_amount}),
            "portal_kind": "employer",
        },
    )


@login_required
@require_http_methods(["POST"])
def employer_submit_payment_proof(request, invoice_id):
    guard = _employer_guard(request)
    if guard:
        return guard

    invoice = get_invoice_for_employer(request.user, invoice_id)
    if not invoice:
        raise Http404("Invoice not found")

    form = PaymentProofForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Payment proof form is invalid.")
        return render(
            request,
            "payments/employer_invoice_detail.html",
            {"invoice": invoice, "proof_form": form, "portal_kind": "employer"},
            status=400,
        )

    try:
        submit_payment_proof(
            invoice=invoice,
            employer_user=request.user,
            method=form.cleaned_data["method"],
            amount=form.cleaned_data["amount"],
            payer_reference=form.cleaned_data.get("payer_reference", ""),
            note=form.cleaned_data.get("note", ""),
            document_url=form.cleaned_data.get("document_url", ""),
        )
        messages.success(request, "Payment proof submitted successfully.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("payments:employer_invoice_detail", invoice_id=invoice.id)


@login_required
@require_http_methods(["GET"])
def worker_earnings(request):
    guard = _helper_guard(request)
    if guard:
        return guard

    invoices = get_helper_invoices(request.user)
    summary = get_helper_earnings_summary(request.user)
    return render(
        request,
        "payments/worker_earnings.html",
        {
            "invoices": invoices,
            "summary": summary,
            "portal_kind": "worker",
        },
    )


@login_required
@require_http_methods(["GET"])
def operations_payments_review(request):
    guard = _operations_guard(request)
    if guard:
        return guard

    payments = get_submitted_payments_for_operations()
    payout_invoices = get_invoices_ready_for_payout()
    return render(
        request,
        "payments/operations_payments_review.html",
        {
            "payments": payments,
            "payout_invoices": payout_invoices,
            "payout_form": OperationsPayoutForm(),
            "portal_kind": "operations",
        },
    )


@login_required
@require_http_methods(["POST"])
def operations_verify_payment(request, payment_id):
    guard = _operations_guard(request)
    if guard:
        return guard

    payment = get_payment_for_operations(payment_id)
    if not payment:
        raise Http404("Payment not found")
    try:
        verify_payment_submission(payment=payment, reviewed_by=request.user)
        messages.success(request, "Payment verified.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("payments:operations_payments_review")


@login_required
@require_http_methods(["POST"])
def operations_reject_payment(request, payment_id):
    guard = _operations_guard(request)
    if guard:
        return guard

    payment = get_payment_for_operations(payment_id)
    if not payment:
        raise Http404("Payment not found")
    try:
        reject_payment_submission(payment=payment, reviewed_by=request.user)
        messages.success(request, "Payment rejected.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("payments:operations_payments_review")


@login_required
@require_http_methods(["POST"])
def operations_mark_paid_out(request, invoice_id):
    guard = _operations_guard(request)
    if guard:
        return guard

    invoice = get_invoice_for_operations(invoice_id)
    if not invoice:
        raise Http404("Invoice not found")
    form = OperationsPayoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Payout form is invalid.")
        return redirect("payments:operations_payments_review")

    try:
        mark_invoice_paid_out(
            invoice=invoice,
            reviewed_by=request.user,
            payout_reference=form.cleaned_data.get("payout_reference", ""),
            note=form.cleaned_data.get("note", ""),
        )
        messages.success(request, "Invoice marked as paid out to worker.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("payments:operations_payments_review")


@login_required
@require_http_methods(["GET"])
def operations_payout_history(request):
    guard = _operations_guard(request)
    if guard:
        return guard
    logs = get_payout_audit_logs()
    return render(
        request,
        "payments/operations_payout_history.html",
        {"logs": logs, "portal_kind": "operations"},
    )


@login_required
@require_http_methods(["GET"])
def operations_payout_history_csv(request):
    guard = _operations_guard(request)
    if guard:
        return guard
    logs = get_payout_audit_logs()

    def _safe(value):
        return str(value).replace('"', '""')

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="mongikazi_payout_history.csv"'
    header = [
        "invoice_number",
        "booking_reference",
        "employer_email",
        "helper_email",
        "worker_fee",
        "platform_fee",
        "total_amount",
        "invoice_status",
        "payout_status",
        "paid_at",
        "paid_out_at",
        "paid_out_by",
        "payout_reference",
        "audit_action",
        "audit_actor",
        "audit_created_at",
        "audit_note",
    ]
    response.write(",".join(header) + "\n")
    for log in logs:
        invoice = log.invoice
        row = [
            invoice.invoice_number,
            invoice.booking.booking_reference,
            invoice.employer_user.email,
            invoice.helper_user.email,
            invoice.worker_fee_amount,
            invoice.platform_fee_amount,
            invoice.total_amount,
            invoice.status,
            invoice.payout_status,
            invoice.paid_at.isoformat() if invoice.paid_at else "",
            invoice.paid_out_at.isoformat() if invoice.paid_out_at else "",
            invoice.paid_out_by.email if invoice.paid_out_by else "",
            invoice.payout_reference or "",
            log.action,
            log.performed_by.email if log.performed_by else "",
            log.created_at.isoformat(),
            log.note or "",
        ]
        escaped = [f'"{_safe(v)}"' for v in row]
        response.write(",".join(escaped) + "\n")
    return response

