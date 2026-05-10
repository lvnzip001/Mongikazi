from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EmployerLocationForm, EmployerServiceForm, HelperProfileForm, HelperServicesForm, HelperTrustForm
from .selectors.onboarding_selectors import get_onboarding_progress
from .services.onboarding_service import (
    complete_employer_onboarding,
    complete_helper_onboarding,
    get_or_create_employer_onboarding_profile,
    get_or_create_helper_onboarding_profile,
    user_can_access_employer_onboarding,
    user_can_access_helper_onboarding,
)
from .services.redirect_service import redirect_user_to_correct_onboarding_flow


def _base_context(request, *, step_label="", step_number=0):
    return {
        "step_label": step_label,
        "step_number": step_number,
        "progress": get_onboarding_progress(request.user),
    }


def _deny_role_access(request):
    messages.warning(request, "This onboarding step is not available for your account type.")
    return redirect("onboarding:start")


@login_required
@require_http_methods(["GET"])
def start(request):
    return redirect(redirect_user_to_correct_onboarding_flow(request.user))


@login_required
@require_http_methods(["GET", "POST"])
def employer_service(request):
    if not user_can_access_employer_onboarding(request.user):
        return _deny_role_access(request)
    if request.user.is_onboarding_complete:
        return redirect("accounts:account_pending")

    profile = get_or_create_employer_onboarding_profile(request.user)
    form = EmployerServiceForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("onboarding:employer_location")

    return render(
        request,
        "onboarding/employer_step_1.html",
        {**_base_context(request, step_label="Step 1 of 2", step_number=1), "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def employer_location(request):
    if not user_can_access_employer_onboarding(request.user):
        return _deny_role_access(request)
    if request.user.is_onboarding_complete:
        return redirect("accounts:account_pending")

    profile = get_or_create_employer_onboarding_profile(request.user)
    form = EmployerLocationForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("onboarding:employer_complete")

    return render(
        request,
        "onboarding/employer_step_2.html",
        {**_base_context(request, step_label="Step 2 of 2", step_number=2), "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def employer_complete(request):
    if not user_can_access_employer_onboarding(request.user):
        return _deny_role_access(request)

    profile = get_or_create_employer_onboarding_profile(request.user)
    if request.method == "POST":
        profile = complete_employer_onboarding(request.user)
        messages.success(request, "Employer onboarding completed.")

    return render(
        request,
        "onboarding/employer_complete.html",
        {
            **_base_context(request, step_label="Complete", step_number=2),
            "profile": profile,
            "is_completed": profile.is_completed,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def helper_profile(request):
    if not user_can_access_helper_onboarding(request.user):
        return _deny_role_access(request)
    if request.user.is_onboarding_complete:
        return redirect("accounts:account_pending")

    profile = get_or_create_helper_onboarding_profile(request.user)
    form = HelperProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("onboarding:helper_services")

    return render(
        request,
        "onboarding/helper_step_1.html",
        {**_base_context(request, step_label="Step 1 of 3", step_number=1), "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def helper_services(request):
    if not user_can_access_helper_onboarding(request.user):
        return _deny_role_access(request)
    if request.user.is_onboarding_complete:
        return redirect("accounts:account_pending")

    profile = get_or_create_helper_onboarding_profile(request.user)
    form = HelperServicesForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("onboarding:helper_trust")

    return render(
        request,
        "onboarding/helper_step_2.html",
        {**_base_context(request, step_label="Step 2 of 3", step_number=2), "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def helper_trust(request):
    if not user_can_access_helper_onboarding(request.user):
        return _deny_role_access(request)
    if request.user.is_onboarding_complete:
        return redirect("accounts:account_pending")

    profile = get_or_create_helper_onboarding_profile(request.user)
    form = HelperTrustForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("onboarding:helper_complete")

    return render(
        request,
        "onboarding/helper_step_3.html",
        {**_base_context(request, step_label="Step 3 of 3", step_number=3), "form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def helper_complete(request):
    if not user_can_access_helper_onboarding(request.user):
        return _deny_role_access(request)

    profile = get_or_create_helper_onboarding_profile(request.user)
    if request.method == "POST":
        profile = complete_helper_onboarding(request.user)
        messages.success(request, "Helper onboarding completed.")

    return render(
        request,
        "onboarding/helper_complete.html",
        {
            **_base_context(request, step_label="Complete", step_number=3),
            "profile": profile,
            "is_completed": profile.is_completed,
        },
    )


@login_required
@require_http_methods(["GET"])
def onboarding_complete(request):
    return render(request, "onboarding/onboarding_complete.html", _base_context(request, step_label="Complete"))
