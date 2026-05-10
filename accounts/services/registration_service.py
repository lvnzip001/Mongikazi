from django.contrib.auth import login
from django.utils import timezone

from .redirect_service import get_role_redirect_url


def complete_registration(request, form):
    """Persist a new user, sign them in, and return their next destination."""
    user = form.save(commit=False)
    if user.accepted_terms and user.accepted_terms_at is None:
        user.accepted_terms_at = timezone.now()
    user.save()
    form.save_m2m()
    login(request, user)
    return user, get_role_redirect_url(user)
