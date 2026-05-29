from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EmployerLocationForm, EmployerProfileForm, EmployerServicePreferenceForm
from .models import EmployerLocation
from .selectors.employer_selectors import (
    get_employer_profile_for_user,
    get_employer_profile_preview_context,
    get_employer_service_preferences,
    get_employer_trust_signals,
    get_primary_employer_location,
)
from .services.employer_profile_service import get_or_create_employer_profile_for_user, refresh_employer_profile_state
from .services.onboarding_handoff_service import create_or_update_employer_profile_from_onboarding


def _employer_access_guard(request, require_onboarding=True):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_employer", False):
        return redirect("onboarding:start")
    if require_onboarding and not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _build_missing_items(profile):
    items = []
    if not profile:
        return [
            "Basic employer profile",
            "Primary location",
            "Service preferences",
            "Contact preference",
        ]

    if not (profile.display_name and profile.employer_type and profile.primary_area):
        items.append("Basic employer profile")
    if not profile.locations.filter(is_active=True).exists():
        items.append("Primary location")
    has_preferences = profile.service_preferences.filter(service_type__gt="", service_frequency__gt="").exists()
    if not has_preferences:
        items.append("Service preferences")
    if not (profile.contact_number and profile.preferred_contact_method):
        items.append("Contact preference")
    return items


@login_required
@require_http_methods(["GET"])
def profile_detail(request):
    guard = _employer_access_guard(request)
    if guard:
        return guard

    profile = get_employer_profile_for_user(request.user)
    if not profile:
        try:
            profile = create_or_update_employer_profile_from_onboarding(request.user)
        except ValidationError:
            return redirect("employers:profile_incomplete")

    location = get_primary_employer_location(profile)
    preference = get_employer_service_preferences(profile).first()
    trust_signals = get_employer_trust_signals(profile)

    return render(
        request,
        "employers/profile_detail.html",
        {
            "profile": profile,
            "location": location,
            "preference": preference,
            "trust_signals": trust_signals,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    guard = _employer_access_guard(request)
    if guard:
        return guard

    profile = get_or_create_employer_profile_for_user(request.user)
    form = EmployerProfileForm(request.POST or None, request.FILES or None, instance=profile, user=request.user)
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        refresh_employer_profile_state(profile)
        messages.success(request, "Employer profile updated.")
        return redirect("employers:profile_detail")

    return render(request, "employers/profile_edit.html", {"form": form, "profile": profile})


@login_required
@require_http_methods(["GET", "POST"])
def locations(request):
    guard = _employer_access_guard(request)
    if guard:
        return guard

    profile = get_or_create_employer_profile_for_user(request.user)
    location = get_primary_employer_location(profile) or EmployerLocation(employer=profile)
    form = EmployerLocationForm(
        request.POST or None,
        instance=location,
        user=request.user,
        employer_profile=profile,
    )

    if request.method == "POST" and form.is_valid():
        location = form.save(commit=False)
        location.employer = profile
        location.is_active = True
        if location.is_primary:
            profile.locations.exclude(pk=location.pk).update(is_primary=False)
        location.save()

        profile.primary_location_label = location.label or profile.primary_location_label
        profile.primary_area = location.suburb or location.city or profile.primary_area
        profile.save(update_fields=["primary_location_label", "primary_area", "updated_at"])

        refresh_employer_profile_state(profile)
        messages.success(request, "Primary location updated.")
        return redirect("employers:locations")

    return render(request, "employers/locations.html", {"form": form, "profile": profile, "location": location})


@login_required
@require_http_methods(["GET", "POST"])
def preferences(request):
    guard = _employer_access_guard(request)
    if guard:
        return guard

    profile = get_or_create_employer_profile_for_user(request.user)
    preference = get_employer_service_preferences(profile).first()
    form = EmployerServicePreferenceForm(request.POST or None, instance=preference, user=request.user)

    if request.method == "POST" and form.is_valid():
        preference = form.save(commit=False)
        preference.employer = profile
        preference.save()
        profile.service_preferences.exclude(pk=preference.pk).delete()
        refresh_employer_profile_state(profile)
        messages.success(request, "Service preferences updated.")
        return redirect("employers:preferences")

    return render(request, "employers/preferences.html", {"form": form, "profile": profile, "preference": preference})


@login_required
@require_http_methods(["GET"])
def profile_preview(request):
    guard = _employer_access_guard(request)
    if guard:
        return guard

    profile = get_employer_profile_for_user(request.user)
    if not profile:
        return redirect("employers:profile_incomplete")

    context = get_employer_profile_preview_context(profile)
    return render(request, "employers/profile_preview.html", context)


@login_required
@require_http_methods(["GET"])
def profile_incomplete(request):
    guard = _employer_access_guard(request, require_onboarding=False)
    if guard:
        return guard

    profile = get_employer_profile_for_user(request.user)
    if not profile and request.user.is_onboarding_complete:
        try:
            profile = create_or_update_employer_profile_from_onboarding(request.user)
        except ValidationError:
            profile = None

    missing_items = _build_missing_items(profile)
    return render(
        request,
        "employers/profile_incomplete.html",
        {
            "profile": profile,
            "missing_items": missing_items,
            "onboarding_complete": request.user.is_onboarding_complete,
        },
    )