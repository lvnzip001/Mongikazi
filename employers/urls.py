from django.urls import path

from . import views

app_name = "employers"

urlpatterns = [
    path("profile/", views.profile_detail, name="profile_detail"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/locations/", views.locations, name="locations"),
    path("profile/preferences/", views.preferences, name="preferences"),
    path("profile/preview/", views.profile_preview, name="profile_preview"),
    path("profile/incomplete/", views.profile_incomplete, name="profile_incomplete"),
]