from django.urls import path

from . import views

app_name = "helpers"

urlpatterns = [
    path("profile/", views.profile_detail, name="profile_detail"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/skills/", views.skills, name="skills"),
    path("profile/availability/", views.availability, name="availability"),
    path("profile/preview/", views.profile_preview, name="profile_preview"),
    path("profile/incomplete/", views.profile_incomplete, name="profile_incomplete"),
]
