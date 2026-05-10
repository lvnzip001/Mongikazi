from django.urls import path

from . import views

app_name = "onboarding"

urlpatterns = [
    path("start/", views.start, name="start"),
    path("employer/service/", views.employer_service, name="employer_service"),
    path("employer/location/", views.employer_location, name="employer_location"),
    path("employer/complete/", views.employer_complete, name="employer_complete"),
    path("helper/profile/", views.helper_profile, name="helper_profile"),
    path("helper/services/", views.helper_services, name="helper_services"),
    path("helper/trust/", views.helper_trust, name="helper_trust"),
    path("helper/complete/", views.helper_complete, name="helper_complete"),
    path("complete/", views.onboarding_complete, name="onboarding_complete"),
]
