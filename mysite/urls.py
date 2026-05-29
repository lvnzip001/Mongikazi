"""
URL configuration for mongikazi project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("onboarding/", include(("onboarding.urls", "onboarding"), namespace="onboarding")),
    path("helpers/", include(("helpers.urls", "helpers"), namespace="helpers")),
    path("bookings/", include(("bookings.urls", "bookings"), namespace="bookings")),
    path("messages/", include(("messaging.urls", "messaging"), namespace="messaging")),
    path("payments/", include(("payments.urls", "payments"), namespace="payments")),
    path("employer/", include(("employer_portal.urls", "employer_portal"), namespace="employer_portal")),
    path("worker/", include(("worker_portal.urls", "worker_portal"), namespace="worker_portal")),
    path("employers/", include(("employers.urls", "employers"), namespace="employers")),
    path("locations/", include(("locations.urls", "locations"), namespace="locations")),
    path("", include(("website.urls", "website"), namespace="website")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
