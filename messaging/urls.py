from django.urls import path

from messaging import views

app_name = "messaging"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("thread/<int:thread_id>/", views.thread_detail, name="thread_detail"),
    path("thread/<int:thread_id>/send/", views.send_thread_message, name="send_thread_message"),
    path("booking/<str:booking_reference>/open/", views.open_booking_thread, name="open_booking_thread"),
]

