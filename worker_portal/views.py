from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from worker_portal.services.dashboard_service import build_worker_dashboard_context


def _portal_access_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_helper", False):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _base_context(nav_active):
    return {
        "nav_active": nav_active,
        "work_profile_url": "/helpers/profile/",
    }


@login_required
@require_http_methods(["GET"])
def dashboard(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    context = {**_base_context("dashboard"), **build_worker_dashboard_context(request.user)}
    return render(request, "worker_portal/dashboard.html", context)


@login_required
@require_http_methods(["GET"])
def requests(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(request, "worker_portal/requests.html", _base_context("requests"))


@login_required
@require_http_methods(["GET"])
def jobs(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(request, "worker_portal/jobs.html", _base_context("jobs"))


@login_required
@require_http_methods(["GET"])
def earnings(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return redirect("payments:worker_earnings")


@login_required
@require_http_methods(["GET"])
def messages(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return redirect("messaging:inbox")


@login_required
@require_http_methods(["GET"])
def verification(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    context = {**_base_context("verification"), **build_worker_dashboard_context(request.user)}
    return render(request, "worker_portal/verification.html", context)


@login_required
@require_http_methods(["GET"])
def reviews(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    context = {**_base_context("reviews"), **build_worker_dashboard_context(request.user)}
    return render(request, "worker_portal/reviews.html", context)


@login_required
@require_http_methods(["GET"])
def safety(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(request, "worker_portal/safety.html", _base_context("safety"))


@login_required
@require_http_methods(["GET"])
def coming_soon(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(
        request,
        "worker_portal/coming_soon.html",
        {
            **_base_context("coming_soon"),
            "title": "Feature coming soon",
            "description": "This worker experience is being prepared and will roll out in a future release.",
        },
    )
