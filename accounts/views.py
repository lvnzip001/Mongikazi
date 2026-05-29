from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .forms import MongiKaziLoginForm, RegisterForm
from .models import User
from .services.redirect_service import get_onboarding_url, get_public_home_url, get_role_redirect_url
from .services.registration_service import complete_registration


def _safe_next_url(request):
    candidate = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return ""


def _auth_base_context():
    return {"public_home_url": get_public_home_url()}


@require_http_methods(["GET"])
def role_select(request):
    if request.user.is_authenticated:
        return redirect(get_role_redirect_url(request.user))
    return render(request, "accounts/role_select.html", _auth_base_context())


@require_http_methods(["GET", "POST"])
def register(request, role):
    role = role.upper()
    valid_roles = {User.Role.EMPLOYER, User.Role.HELPER}
    if role not in valid_roles:
        messages.warning(request, "Please choose whether you need help or want work.")
        return redirect("accounts:role_select")

    if request.user.is_authenticated:
        return redirect(get_role_redirect_url(request.user))

    form = RegisterForm(request.POST or None, request.FILES or None, role=role)
    if request.method == "POST" and form.is_valid():
        _, next_url = complete_registration(request, form)
        return redirect(next_url)

    context = {
        **_auth_base_context(),
        "form": form,
        "role": role,
        "is_employer": role == User.Role.EMPLOYER,
        "page_title": "Create your employer account" if role == User.Role.EMPLOYER else "Create your helper profile",
    }
    return render(request, "accounts/register.html", context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(get_role_redirect_url(request.user))

    next_url = _safe_next_url(request)
    form = MongiKaziLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if next_url:
            return redirect(next_url)
        return redirect(get_role_redirect_url(form.get_user()))

    return render(request, "accounts/login.html", {**_auth_base_context(), "form": form, "next": next_url})


@login_required
@require_http_methods(["GET"])
def account_pending(request):
    role_label = "Operations" if getattr(request.user, "is_operations_user", False) else "Account"
    if getattr(request.user, "is_employer", False):
        role_label = "Employer"
    elif getattr(request.user, "is_helper", False):
        role_label = "Helper"

    portal_url = get_role_redirect_url(request.user)
    next_url = portal_url if request.user.is_onboarding_complete else get_onboarding_url(request.user)

    return render(
        request,
        "accounts/account_pending.html",
        {
            **_auth_base_context(),
            "next_url": next_url,
            "portal_url": portal_url,
            "is_employer": getattr(request.user, "is_employer", False),
            "is_helper": getattr(request.user, "is_helper", False),
            "is_operations": getattr(request.user, "is_operations_user", False),
            "role_label": role_label,
        },
    )


@require_http_methods(["GET"])
def password_reset_placeholder(request):
    return render(request, "accounts/password_reset.html", _auth_base_context())


@require_http_methods(["GET"])
def logout_confirm(request):
    return render(request, "accounts/logout_confirm.html", _auth_base_context())


@require_POST
def logout_view(request):
    logout(request)
    return redirect(get_public_home_url())

