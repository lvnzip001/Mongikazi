from django.urls import path

from payments import views

app_name = "payments"

urlpatterns = [
    path("employer/invoices/", views.employer_invoices, name="employer_invoices"),
    path("employer/invoices/<int:invoice_id>/", views.employer_invoice_detail, name="employer_invoice_detail"),
    path("employer/invoices/<int:invoice_id>/submit-proof/", views.employer_submit_payment_proof, name="employer_submit_payment_proof"),
    path("worker/earnings/", views.worker_earnings, name="worker_earnings"),
    path("operations/review/", views.operations_payments_review, name="operations_payments_review"),
    path("operations/review/<int:payment_id>/verify/", views.operations_verify_payment, name="operations_verify_payment"),
    path("operations/review/<int:payment_id>/reject/", views.operations_reject_payment, name="operations_reject_payment"),
    path("operations/review/invoice/<int:invoice_id>/paid-out/", views.operations_mark_paid_out, name="operations_mark_paid_out"),
    path("operations/payout-history/", views.operations_payout_history, name="operations_payout_history"),
    path("operations/payout-history/export.csv", views.operations_payout_history_csv, name="operations_payout_history_csv"),
]




