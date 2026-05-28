from django.urls import path

from . import views

app_name = "employer_portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("find-help/", views.find_help, name="find_help"),
    path("bookings/", views.bookings, name="bookings"),
    path("favourites/", views.favourites, name="favourites"),
    path("payments/", views.payments, name="payments"),
    path("messages/", views.messages, name="messages"),
    path("support/", views.support, name="support"),
    path("coming-soon/", views.coming_soon, name="coming_soon"),
]