from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from employer_portal.services.dashboard_service import build_employer_dashboard_context


def _portal_access_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_employer", False):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _base_context(request, nav_active):
    return {
        "nav_active": nav_active,
        "profile_url": "/employers/profile/",
    }


@login_required
@require_http_methods(["GET"])
def dashboard(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard

    context = {
        **_base_context(request, "dashboard"),
        **build_employer_dashboard_context(request.user),
    }
    return render(request, "employer_portal/dashboard.html", context)


@login_required
@require_http_methods(["GET"])
def find_help(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard

    context = {
        **_base_context(request, "find_help"),
        **build_employer_dashboard_context(request.user),
    }
    return render(request, "employer_portal/find_help.html", context)


@login_required
@require_http_methods(["GET"])
def bookings(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(request, "employer_portal/bookings.html", _base_context(request, "bookings"))


@login_required
@require_http_methods(["GET"])
def favourites(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(request, "employer_portal/favourites.html", _base_context(request, "favourites"))


@login_required
@require_http_methods(["GET"])
def payments(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return redirect("payments:employer_invoices")


@login_required
@require_http_methods(["GET"])
def messages(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return redirect("messaging:inbox")


@login_required
@require_http_methods(["GET"])
def support(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(request, "employer_portal/support.html", _base_context(request, "support"))


@login_required
@require_http_methods(["GET"])
def coming_soon(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return render(
        request,
        "employer_portal/coming_soon.html",
        {
            **_base_context(request, "coming_soon"),
            "title": "Feature coming soon",
            "description": "This experience is being prepared and will roll out in a future release.",
        },
    )
