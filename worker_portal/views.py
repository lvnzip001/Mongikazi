from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from helpers.forms import WorkerVerificationUploadForm
from helpers.models import WorkerVerificationDocument
from helpers.selectors.helper_selectors import get_helper_profile_for_user
from helpers.selectors.verification_selectors import get_current_verification_documents, get_worker_verification_page_context
from helpers.services.verification_service import upload_worker_verification_document
from bookings.selectors.worker_opportunities_selectors import get_worker_opportunities_context
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
    context = {
        **_base_context("dashboard"),
        "portal_kind": "worker",
        **build_worker_dashboard_context(request.user),
    }
    return render(request, "worker_portal/dashboard.html", context)


@login_required
@require_http_methods(["GET"])
def offers(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    context = {
        **_base_context("offers"),
        "portal_kind": "worker",
        **get_worker_opportunities_context(request.user, preview_limit=50),
    }
    return render(request, "worker_portal/offers.html", context)


@login_required
@require_http_methods(["GET"])
def requests(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    return redirect("worker_portal:offers")


@login_required
@require_http_methods(["GET"])
def jobs(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard
    context = {
        **_base_context("jobs"),
        "portal_kind": "worker",
        **get_worker_opportunities_context(request.user, preview_limit=5),
    }
    return render(request, "worker_portal/jobs.html", context)


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
    context = {
        **_base_context("verification"),
        **get_worker_verification_page_context(request.user),
    }
    return render(request, "worker_portal/verification.html", context)


@login_required
@require_http_methods(["POST"])
def verification_upload(request):
    guard = _portal_access_guard(request)
    if guard:
        return guard

    form = WorkerVerificationUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        for error in form.errors.get("file", []) + form.errors.get("document_type", []) + form.non_field_errors():
            django_messages.error(request, error)
        return redirect("worker_portal:verification")

    try:
        upload_worker_verification_document(
            user=request.user,
            document_type=form.cleaned_data["document_type"],
            uploaded_file=form.cleaned_data["file"],
        )
        django_messages.success(request, "Document uploaded. It will be reviewed by our team.")
    except ValidationError as exc:
        django_messages.error(request, exc.message if hasattr(exc, "message") else str(exc))

    return redirect("worker_portal:verification")


@login_required
@require_http_methods(["GET"])
def verification_document_download(request, document_type):
    guard = _portal_access_guard(request)
    if guard:
        return guard

    if document_type not in WorkerVerificationDocument.DocumentType.values:
        raise Http404("Document not found")

    from helpers.selectors.helper_selectors import get_helper_profile_for_user

    helper_profile = get_helper_profile_for_user(request.user)
    if not helper_profile:
        raise Http404("Document not found")

    documents = get_current_verification_documents(helper_profile)
    document = documents.get(document_type)
    if not document or not document.file:
        raise Http404("Document not found")

    return FileResponse(document.file.open("rb"), as_attachment=True, filename=document.file.name.split("/")[-1])


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
