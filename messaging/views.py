from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from bookings.models import Booking
from messaging.forms import MessageSendForm
from messaging.selectors.messaging_selectors import (
    get_thread_for_user,
    get_thread_messages,
    get_threads_for_employer,
    get_threads_for_helper,
    get_unread_counts_for_user,
)
from messaging.services.messaging_service import mark_thread_read, open_or_get_thread_for_booking, send_message


def _role_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not (getattr(request.user, "is_employer", False) or getattr(request.user, "is_helper", False)):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _nav_context(user):
    role = "employer" if getattr(user, "is_employer", False) else "helper"
    return {
        "role_kind": role,
        "dashboard_url": reverse("employer_portal:dashboard") if role == "employer" else reverse("worker_portal:dashboard"),
        "bookings_url": reverse("bookings:employer_bookings") if role == "employer" else reverse("bookings:worker_requests"),
    }


def _threads_for_user(user):
    if getattr(user, "is_employer", False):
        return get_threads_for_employer(user)
    return get_threads_for_helper(user)


@login_required
@require_http_methods(["GET"])
def inbox(request):
    guard = _role_guard(request)
    if guard:
        return guard

    threads = _threads_for_user(request.user)
    return render(
        request,
        "messaging/inbox.html",
        {
            "threads": threads,
            "selected_thread": None,
            "message_form": MessageSendForm(),
            "unread": get_unread_counts_for_user(request.user),
            **_nav_context(request.user),
        },
    )


@login_required
@require_http_methods(["GET"])
def thread_detail(request, thread_id):
    guard = _role_guard(request)
    if guard:
        return guard

    thread = get_thread_for_user(thread_id, request.user)
    if not thread:
        raise Http404("Thread not found")

    mark_thread_read(thread=thread, reader=request.user)
    thread_messages = get_thread_messages(thread)

    return render(
        request,
        "messaging/inbox.html",
        {
            "threads": _threads_for_user(request.user),
            "selected_thread": thread,
            "thread_messages": thread_messages,
            "message_form": MessageSendForm(),
            "unread": get_unread_counts_for_user(request.user),
            **_nav_context(request.user),
        },
    )


@login_required
@require_http_methods(["POST"])
def send_thread_message(request, thread_id):
    guard = _role_guard(request)
    if guard:
        return guard

    thread = get_thread_for_user(thread_id, request.user)
    if not thread:
        raise Http404("Thread not found")

    form = MessageSendForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Message cannot be empty.")
        return redirect("messaging:thread_detail", thread_id=thread.id)

    try:
        send_message(thread=thread, sender=request.user, body=form.cleaned_data["body"])
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("messaging:thread_detail", thread_id=thread.id)


@login_required
@require_http_methods(["GET"])
def open_booking_thread(request, booking_reference):
    guard = _role_guard(request)
    if guard:
        return guard

    booking = (
        Booking.objects.select_related("employer__user", "worker__user")
        .filter(booking_reference=booking_reference)
        .first()
    )
    if not booking:
        raise Http404("Booking not found")

    try:
        thread = open_or_get_thread_for_booking(booking=booking, actor=request.user)
    except ValidationError as exc:
        messages.error(request, exc.message)
        if getattr(request.user, "is_employer", False):
            return redirect("bookings:employer_booking_detail", booking_reference=booking_reference)
        return redirect("bookings:worker_request_detail", booking_reference=booking_reference)

    return redirect("messaging:thread_detail", thread_id=thread.id)

