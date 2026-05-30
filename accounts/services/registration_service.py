from django.conf import settings
from django.contrib.auth import login
from django.utils import timezone

from accounts.models import UserPolicyAcceptance
from .redirect_service import get_role_redirect_url


def _get_request_ip(request):
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip() or None


def complete_registration(request, form):
    """Persist a new user, sign them in, and return their next destination."""
    user = form.save(commit=False)
    if user.accepted_terms and user.accepted_terms_at is None:
        user.accepted_terms_at = timezone.now()
    user.save()
    form.save_m2m()
    if user.accepted_terms:
        UserPolicyAcceptance.objects.create(
            user=user,
            source=UserPolicyAcceptance.Source.REGISTRATION,
            terms_version=settings.MONGIKAZI_TERMS_VERSION,
            privacy_version=settings.MONGIKAZI_PRIVACY_VERSION,
            safety_version=settings.MONGIKAZI_SAFETY_VERSION,
            ip_address=_get_request_ip(request),
            user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:512],
        )
    login(request, user)
    return user, get_role_redirect_url(user)
