from django.urls import reverse


def portal_navigation(request):
    """Shared portal URLs and active nav hints for profile shells."""
    ctx = {
        "work_profile_url": reverse("helpers:profile_detail"),
        "employer_profile_url": reverse("employers:profile_detail"),
        "worker_dashboard_url": reverse("worker_portal:dashboard"),
        "employer_dashboard_url": reverse("employer_portal:dashboard"),
    }

    match = getattr(request, "resolver_match", None)
    if not match:
        return ctx

    if match.app_name == "helpers":
        ctx["nav_active"] = "profile"
        ctx["profile_nav_active"] = match.url_name
        ctx["portal_section"] = "worker"
    elif match.app_name == "employers":
        ctx["nav_active"] = "profile"
        ctx["profile_nav_active"] = match.url_name
        ctx["portal_section"] = "employer"

    return ctx
