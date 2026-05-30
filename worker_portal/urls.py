from django.urls import path

from . import views

app_name = "worker_portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("requests/", views.requests, name="requests"),
    path("jobs/", views.jobs, name="jobs"),
    path("earnings/", views.earnings, name="earnings"),
    path("messages/", views.messages, name="messages"),
    path("verification/", views.verification, name="verification"),
    path("verification/upload/", views.verification_upload, name="verification_upload"),
    path(
        "verification/document/<str:document_type>/",
        views.verification_document_download,
        name="verification_document_download",
    ),
    path("reviews/", views.reviews, name="reviews"),
    path("safety/", views.safety, name="safety"),
    path("coming-soon/", views.coming_soon, name="coming_soon"),
]