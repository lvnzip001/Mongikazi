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
    path("reviews/", views.reviews, name="reviews"),
    path("safety/", views.safety, name="safety"),
    path("coming-soon/", views.coming_soon, name="coming_soon"),
]