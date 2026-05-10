from django.forms import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import HelperAvailabilityForm, HelperProfileForm, HelperSkillForm
from .selectors.helper_selectors import (
    get_helper_availability,
    get_helper_profile_for_user,
    get_helper_profile_preview_context,
    get_helper_skills,
    get_helper_trust_signals,
)
from .services.helper_profile_service import get_or_create_helper_profile_for_user, refresh_helper_profile_state
from .services.onboarding_handoff_service import (
    create_or_update_helper_profile_from_onboarding,
    ensure_default_service_categories,
)


def _helper_access_guard(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if not getattr(request.user, "is_helper", False):
        return redirect("onboarding:start")
    if not request.user.is_onboarding_complete:
        return redirect("onboarding:start")
    return None


def _build_missing_items(profile):
    items = []
    if not (profile.display_name and profile.location and profile.bio):
        items.append("Basic profile details")
    if not profile.skills.exists():
        items.append("At least one service skill")
    if not (profile.availability_summary or profile.availability.exists()):
        items.append("Availability details")
    if profile.trust_signals.count() < 3:
        items.append("Trust readiness signals")
    return items


@login_required
@require_http_methods(["GET"])
def profile_detail(request):
    guard = _helper_access_guard(request)
    if guard:
        return guard

    profile = get_helper_profile_for_user(request.user)
    if not profile:
        try:
            profile = create_or_update_helper_profile_from_onboarding(request.user)
        except ValidationError:
            return redirect("helpers:profile_incomplete")

    skills = get_helper_skills(profile)
    availability = get_helper_availability(profile)
    trust_signals = get_helper_trust_signals(profile)
    return render(
        request,
        "helpers/profile_detail.html",
        {
            "profile": profile,
            "skills": skills,
            "availability": availability,
            "trust_signals": trust_signals,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    guard = _helper_access_guard(request)
    if guard:
        return guard

    profile = get_or_create_helper_profile_for_user(request.user)
    form = HelperProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        refresh_helper_profile_state(profile)
        messages.success(request, "Profile updated.")
        return redirect("helpers:profile_detail")
    return render(request, "helpers/profile_edit.html", {"form": form, "profile": profile})


@login_required
@require_http_methods(["GET", "POST"])
def skills(request):
    guard = _helper_access_guard(request)
    if guard:
        return guard

    ensure_default_service_categories()
    profile = get_or_create_helper_profile_for_user(request.user)
    form = HelperSkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        skill = form.save(commit=False)
        skill.helper = profile
        existing = profile.skills.filter(category=skill.category).first()
        if existing:
            existing.years_experience = skill.years_experience
            existing.skill_note = skill.skill_note
            existing.is_primary = skill.is_primary
            existing.save()
            skill = existing
        else:
            skill.save()

        if skill.is_primary:
            profile.skills.exclude(pk=skill.pk).update(is_primary=False)
        refresh_helper_profile_state(profile)
        messages.success(request, "Skills updated.")
        return redirect("helpers:skills")

    return render(request, "helpers/skills.html", {"form": form, "profile": profile, "skills": profile.skills.select_related("category")})


@login_required
@require_http_methods(["GET", "POST"])
def availability(request):
    guard = _helper_access_guard(request)
    if guard:
        return guard

    profile = get_or_create_helper_profile_for_user(request.user)
    form = HelperAvailabilityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.helper = profile
        item.save()
        refresh_helper_profile_state(profile)
        messages.success(request, "Availability updated.")
        return redirect("helpers:availability")

    availability_rows = profile.availability.all()
    return render(request, "helpers/availability.html", {"form": form, "profile": profile, "availability_rows": availability_rows})


@login_required
@require_http_methods(["GET"])
def profile_preview(request):
    guard = _helper_access_guard(request)
    if guard:
        return guard

    profile = get_helper_profile_for_user(request.user)
    if not profile:
        return redirect("helpers:profile_incomplete")

    context = get_helper_profile_preview_context(profile)
    return render(request, "helpers/profile_preview.html", context)


@login_required
@require_http_methods(["GET"])
def profile_incomplete(request):
    guard = _helper_access_guard(request)
    if guard:
        return guard

    profile = get_helper_profile_for_user(request.user)
    if not profile:
        try:
            profile = create_or_update_helper_profile_from_onboarding(request.user)
        except ValidationError:
            profile = None

    missing_items = _build_missing_items(profile) if profile else [
        "Basic profile details",
        "At least one service skill",
        "Availability details",
        "Trust readiness signals",
    ]

    return render(request, "helpers/profile_incomplete.html", {"profile": profile, "missing_items": missing_items})
