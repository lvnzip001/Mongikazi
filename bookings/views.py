from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from bookings.forms import (
    BookingApplicationForm,
    EmployerBookingRequestForm,
    EmployerCancelBookingForm,
    WorkerCancelBookingForm,
    WorkerDeclineBookingForm,
)
from bookings.models import Booking, BookingApplication
from bookings.selectors.booking_selectors import (
    get_booking_application_for_employer,
    get_booking_application_for_worker,
    get_booking_applications_for_employer,
    get_booking_events,
    get_booking_for_employer,
    get_booking_for_worker,
    get_employer_bookings,
    get_employer_marketplace_jobs,
    get_worker_applications,
    get_worker_open_marketplace_jobs,
    get_worker_booking_requests,
    get_worker_jobs,
)
from employers.selectors.employer_selectors import build_worker_safe_employer_card
from bookings.services.booking_application_service import (
    apply_to_booking,
    decline_application,
    select_application,
    withdraw_application,
)
from bookings.services.booking_service import create_booking_request
from bookings.services.booking_workflow_service import (
    accept_booking,
    cancel_booking_by_employer,
    cancel_booking_by_worker,
    decline_booking,
    mark_booking_completed,
)
from employers.models import EmployerProfile
from helpers.models import HelperProfile


def _employer_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_employer", False):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _worker_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_helper", False):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _employer_profile_for_user(user):
    return EmployerProfile.objects.filter(user=user, is_active=True).first()


def _worker_profile_for_user(user):
    return HelperProfile.objects.filter(user=user, is_active=True).first()


def _get_employer_booking_or_404(user, booking_reference):
    booking = get_booking_for_employer(user, booking_reference)
    if not booking:
        raise Http404("Booking not found")
    return booking


def _get_worker_booking_or_404(user, booking_reference):
    booking = get_booking_for_worker(user, booking_reference)
    if not booking:
        raise Http404("Booking not found")
    return booking


@login_required
@require_http_methods(["GET"])
def employer_bookings(request):
    guard = _employer_guard(request)
    if guard:
        return guard

    bookings = get_employer_bookings(request.user)
    return render(
        request,
        "bookings/employer_bookings.html",
        {
            "bookings": bookings,
            "nav_active": "employer_bookings",
            "portal_kind": "employer",
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def employer_booking_create(request):
    guard = _employer_guard(request)
    if guard:
        return guard

    employer_profile = _employer_profile_for_user(request.user)
    if not employer_profile:
        messages.warning(request, "Complete your employer profile before creating booking requests.")
        return redirect("employers:profile_incomplete")

    form = EmployerBookingRequestForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        try:
            booking = create_booking_request(
                employer_profile=employer_profile,
                request_type=form.cleaned_data["request_type"],
                worker_profile=form.cleaned_data["worker"],
                service_category=form.cleaned_data["service_category"],
                employer_location=form.cleaned_data["employer_location"],
                scheduled_date=form.cleaned_data["scheduled_date"],
                start_time=form.cleaned_data["start_time"],
                duration_hours=form.cleaned_data["duration_hours"],
                special_instructions=form.cleaned_data.get("special_instructions", ""),
                created_by=request.user,
            )
            if booking.request_type == Booking.RequestType.DIRECT_REQUEST:
                messages.success(request, f"Booking request {booking.booking_reference} sent to worker.")
            else:
                messages.success(request, f"Marketplace job {booking.booking_reference} posted.")
            return redirect("bookings:employer_booking_detail", booking_reference=booking.booking_reference)
        except ValidationError as exc:
            form.add_error(None, exc.message)

    return render(
        request,
        "bookings/employer_booking_create.html",
        {
            "form": form,
            "portal_kind": "employer",
            "nav_active": "employer_create",
        },
    )


@login_required
@require_http_methods(["GET"])
def employer_booking_detail(request, booking_reference):
    guard = _employer_guard(request)
    if guard:
        return guard

    from helpers.selectors.verification_selectors import build_employer_safe_worker_card

    booking = _get_employer_booking_or_404(request.user, booking_reference)
    events = get_booking_events(booking)
    can_cancel = booking.status in [Booking.Status.PENDING_WORKER_RESPONSE, Booking.Status.ACCEPTED]
    can_complete = booking.status == Booking.Status.ACCEPTED
    worker_card = None
    if booking.worker_id:
        worker_card = build_employer_safe_worker_card(booking.worker)

    return render(
        request,
        "bookings/employer_booking_detail.html",
        {
            "booking": booking,
            "worker_card": worker_card,
            "events": events,
            "cancel_form": EmployerCancelBookingForm(),
            "can_cancel": can_cancel,
            "can_complete": can_complete,
            "portal_kind": "employer",
            "nav_active": "employer_bookings",
        },
    )


@login_required
@require_http_methods(["GET"])
def employer_marketplace_jobs(request):
    guard = _employer_guard(request)
    if guard:
        return guard
    jobs = get_employer_marketplace_jobs(request.user)
    return render(
        request,
        "bookings/employer_marketplace_jobs.html",
        {"jobs": jobs, "portal_kind": "employer", "nav_active": "employer_marketplace"},
    )


@login_required
@require_http_methods(["GET"])
def employer_booking_applications(request, booking_reference):
    guard = _employer_guard(request)
    if guard:
        return guard
    booking, application_rows = get_booking_applications_for_employer(request.user, booking_reference)
    if not booking:
        raise Http404("Booking not found")
    return render(
        request,
        "bookings/employer_booking_applications.html",
        {
            "booking": booking,
            "application_rows": application_rows,
            "portal_kind": "employer",
            "nav_active": "employer_marketplace",
        },
    )


@login_required
@require_http_methods(["POST"])
def employer_select_application(request, application_id):
    guard = _employer_guard(request)
    if guard:
        return guard
    application = get_booking_application_for_employer(request.user, application_id)
    if not application:
        raise Http404("Application not found")
    try:
        booking = select_application(application=application, performed_by=request.user)
        messages.success(request, "Applicant selected. Waiting for helper confirmation.")
        return redirect("bookings:employer_booking_detail", booking_reference=booking.booking_reference)
    except ValidationError as exc:
        messages.error(request, exc.message)
        return redirect("bookings:employer_booking_applications", booking_reference=application.booking.booking_reference)


@login_required
@require_http_methods(["POST"])
def employer_decline_application(request, application_id):
    guard = _employer_guard(request)
    if guard:
        return guard
    application = get_booking_application_for_employer(request.user, application_id)
    if not application:
        raise Http404("Application not found")
    try:
        decline_application(application=application, performed_by=request.user)
        messages.success(request, "Application declined.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("bookings:employer_booking_applications", booking_reference=application.booking.booking_reference)


@login_required
@require_http_methods(["POST"])
def employer_cancel_booking(request, booking_reference):
    guard = _employer_guard(request)
    if guard:
        return guard

    booking = _get_employer_booking_or_404(request.user, booking_reference)
    form = EmployerCancelBookingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Cancellation reason is invalid.")
        return redirect("bookings:employer_booking_detail", booking_reference=booking.booking_reference)

    try:
        cancel_booking_by_employer(booking, request.user, reason=form.cleaned_data.get("reason", ""))
        messages.success(request, "Booking cancelled.")
    except ValidationError as exc:
        messages.error(request, exc.message)

    return redirect("bookings:employer_booking_detail", booking_reference=booking.booking_reference)


@login_required
@require_http_methods(["POST"])
def employer_mark_completed(request, booking_reference):
    guard = _employer_guard(request)
    if guard:
        return guard

    booking = _get_employer_booking_or_404(request.user, booking_reference)
    try:
        mark_booking_completed(booking, request.user)
        messages.success(request, "Booking marked as completed.")
    except ValidationError as exc:
        messages.error(request, exc.message)

    return redirect("bookings:employer_booking_detail", booking_reference=booking.booking_reference)


@login_required
@require_http_methods(["GET"])
def worker_requests(request):
    guard = _worker_guard(request)
    if guard:
        return guard

    worker_profile = _worker_profile_for_user(request.user)
    if not worker_profile:
        messages.warning(request, "Complete your worker profile before handling requests.")
        return redirect("helpers:profile_incomplete")

    requests_qs = get_worker_booking_requests(request.user)
    return render(
        request,
        "bookings/worker_requests.html",
        {
            "requests": requests_qs,
            "portal_kind": "worker",
            "nav_active": "worker_requests",
        },
    )


@login_required
@require_http_methods(["GET"])
def worker_jobs(request):
    guard = _worker_guard(request)
    if guard:
        return guard

    jobs = get_worker_jobs(request.user)
    return render(
        request,
        "bookings/worker_jobs.html",
        {
            "jobs": jobs,
            "portal_kind": "worker",
            "nav_active": "worker_jobs",
        },
    )


@login_required
@require_http_methods(["GET"])
def worker_available_jobs(request):
    guard = _worker_guard(request)
    if guard:
        return guard
    jobs = get_worker_open_marketplace_jobs(request.user)
    return render(
        request,
        "bookings/worker_available_jobs.html",
        {"jobs": jobs, "portal_kind": "worker", "nav_active": "worker_available_jobs"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def worker_apply_to_job(request, booking_reference):
    guard = _worker_guard(request)
    if guard:
        return guard
    worker_profile = _worker_profile_for_user(request.user)
    if not worker_profile:
        return redirect("helpers:profile_incomplete")
    booking = (
        Booking.objects.filter(booking_reference=booking_reference)
        .select_related(
            "employer",
            "employer__user",
            "service_category",
            "employer_location",
            "employer_location__locality",
        )
        .first()
    )
    if not booking:
        raise Http404("Booking not found")
    form = BookingApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            apply_to_booking(
                booking=booking,
                worker_profile=worker_profile,
                message=form.cleaned_data.get("message", ""),
                proposed_fee=form.cleaned_data.get("proposed_fee"),
                performed_by=request.user,
            )
            messages.success(request, "Application submitted.")
            return redirect("bookings:worker_my_applications")
        except ValidationError as exc:
            form.add_error(None, exc.message)
    return render(
        request,
        "bookings/worker_apply_to_job.html",
        {
            "booking": booking,
            "employer_card": build_worker_safe_employer_card(booking.employer, booking=booking),
            "form": form,
            "portal_kind": "worker",
            "nav_active": "worker_available_jobs",
        },
    )


@login_required
@require_http_methods(["GET"])
def worker_my_applications(request):
    guard = _worker_guard(request)
    if guard:
        return guard
    applications = get_worker_applications(request.user)
    return render(
        request,
        "bookings/worker_my_applications.html",
        {"applications": applications, "portal_kind": "worker", "nav_active": "worker_applications"},
    )


@login_required
@require_http_methods(["POST"])
def worker_withdraw_application(request, application_id):
    guard = _worker_guard(request)
    if guard:
        return guard
    application = get_booking_application_for_worker(request.user, application_id)
    if not application:
        raise Http404("Application not found")
    try:
        withdraw_application(application=application, performed_by=request.user)
        messages.success(request, "Application withdrawn.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("bookings:worker_my_applications")


@login_required
@require_http_methods(["GET"])
def worker_request_detail(request, booking_reference):
    guard = _worker_guard(request)
    if guard:
        return guard

    booking = _get_worker_booking_or_404(request.user, booking_reference)
    events = get_booking_events(booking)

    return render(
        request,
        "bookings/worker_request_detail.html",
        {
            "booking": booking,
            "events": events,
            "decline_form": WorkerDeclineBookingForm(),
            "cancel_form": WorkerCancelBookingForm(),
            "can_accept": booking.status == Booking.Status.PENDING_WORKER_RESPONSE,
            "can_decline": booking.status == Booking.Status.PENDING_WORKER_RESPONSE,
            "can_cancel": booking.status == Booking.Status.ACCEPTED,
            "portal_kind": "worker",
            "nav_active": "worker_requests",
        },
    )


@login_required
@require_http_methods(["POST"])
def worker_accept_booking(request, booking_reference):
    guard = _worker_guard(request)
    if guard:
        return guard

    booking = _get_worker_booking_or_404(request.user, booking_reference)
    try:
        accept_booking(booking, request.user)
        messages.success(request, "Booking request accepted.")
    except ValidationError as exc:
        messages.error(request, exc.message)

    return redirect("bookings:worker_request_detail", booking_reference=booking.booking_reference)


@login_required
@require_http_methods(["POST"])
def worker_decline_booking(request, booking_reference):
    guard = _worker_guard(request)
    if guard:
        return guard

    booking = _get_worker_booking_or_404(request.user, booking_reference)
    form = WorkerDeclineBookingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Decline reason is invalid.")
        return redirect("bookings:worker_request_detail", booking_reference=booking.booking_reference)

    try:
        decline_booking(booking, request.user, reason=form.cleaned_data.get("reason", ""))
        messages.success(request, "Booking request declined.")
    except ValidationError as exc:
        messages.error(request, exc.message)

    return redirect("bookings:worker_request_detail", booking_reference=booking.booking_reference)


@login_required
@require_http_methods(["POST"])
def worker_cancel_booking(request, booking_reference):
    guard = _worker_guard(request)
    if guard:
        return guard

    booking = _get_worker_booking_or_404(request.user, booking_reference)
    form = WorkerCancelBookingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Cancellation reason is invalid.")
        return redirect("bookings:worker_request_detail", booking_reference=booking.booking_reference)

    try:
        cancel_booking_by_worker(booking, request.user, reason=form.cleaned_data.get("reason", ""))
        messages.success(request, "Booking cancelled.")
    except ValidationError as exc:
        messages.error(request, exc.message)

    return redirect("bookings:worker_request_detail", booking_reference=booking.booking_reference)


@login_required
@require_http_methods(["GET"])
def booking_timeline(request, booking_reference):
    if getattr(request.user, "is_employer", False):
        booking = _get_employer_booking_or_404(request.user, booking_reference)
        nav_active = "employer_bookings"
        portal_kind = "employer"
    elif getattr(request.user, "is_helper", False):
        booking = _get_worker_booking_or_404(request.user, booking_reference)
        nav_active = "worker_requests"
        portal_kind = "worker"
    else:
        return redirect("onboarding:start")

    return render(
        request,
        "bookings/booking_timeline.html",
        {
            "booking": booking,
            "events": get_booking_events(booking),
            "nav_active": nav_active,
            "portal_kind": portal_kind,
        },
    )


@login_required
@require_http_methods(["GET"])
def booking_action_result(request):
    return render(
        request,
        "bookings/booking_action_result.html",
        {
            "portal_kind": "employer" if getattr(request.user, "is_employer", False) else "worker",
            "nav_active": "employer_bookings" if getattr(request.user, "is_employer", False) else "worker_requests",
        },
    )


@login_required
@require_http_methods(["GET"])
def booking_empty_state(request):
    return render(
        request,
        "bookings/booking_empty_state.html",
        {
            "portal_kind": "employer" if getattr(request.user, "is_employer", False) else "worker",
            "nav_active": "employer_bookings" if getattr(request.user, "is_employer", False) else "worker_requests",
        },
    )
