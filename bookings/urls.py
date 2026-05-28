from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("employer/", views.employer_bookings, name="employer_bookings"),
    path("employer/create/", views.employer_booking_create, name="employer_booking_create"),
    path("employer/marketplace/", views.employer_marketplace_jobs, name="employer_marketplace_jobs"),
    path("employer/<str:booking_reference>/", views.employer_booking_detail, name="employer_booking_detail"),
    path(
        "employer/<str:booking_reference>/applications/",
        views.employer_booking_applications,
        name="employer_booking_applications",
    ),
    path("employer/applications/<int:application_id>/select/", views.employer_select_application, name="employer_select_application"),
    path("employer/applications/<int:application_id>/decline/", views.employer_decline_application, name="employer_decline_application"),
    path("employer/<str:booking_reference>/cancel/", views.employer_cancel_booking, name="employer_cancel_booking"),
    path("employer/<str:booking_reference>/complete/", views.employer_mark_completed, name="employer_mark_completed"),
    path("worker/requests/", views.worker_requests, name="worker_requests"),
    path("worker/jobs/", views.worker_jobs, name="worker_jobs"),
    path("worker/marketplace/", views.worker_available_jobs, name="worker_available_jobs"),
    path("worker/marketplace/<str:booking_reference>/apply/", views.worker_apply_to_job, name="worker_apply_to_job"),
    path("worker/applications/", views.worker_my_applications, name="worker_my_applications"),
    path("worker/applications/<int:application_id>/withdraw/", views.worker_withdraw_application, name="worker_withdraw_application"),
    path("worker/requests/<str:booking_reference>/", views.worker_request_detail, name="worker_request_detail"),
    path("worker/requests/<str:booking_reference>/accept/", views.worker_accept_booking, name="worker_accept_booking"),
    path("worker/requests/<str:booking_reference>/decline/", views.worker_decline_booking, name="worker_decline_booking"),
    path("worker/jobs/<str:booking_reference>/cancel/", views.worker_cancel_booking, name="worker_cancel_booking"),
    path("timeline/<str:booking_reference>/", views.booking_timeline, name="booking_timeline"),
    path("action-result/", views.booking_action_result, name="booking_action_result"),
    path("empty-state/", views.booking_empty_state, name="booking_empty_state"),
]
