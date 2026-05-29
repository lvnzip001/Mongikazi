from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path("autocomplete/", views.locality_autocomplete, name="autocomplete"),
]
