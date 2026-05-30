from django.db import transaction
from django.forms import ValidationError
from django.utils import timezone

from helpers.models import HelperProfile, HelperTrustSignal, WorkerVerificationDocument


DOCUMENT_TYPE_TO_SIGNAL = {
    WorkerVerificationDocument.DocumentType.ID_DOCUMENT: HelperTrustSignal.SignalType.ID_DOCUMENT,
    WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK: HelperTrustSignal.SignalType.CRIMINAL_RECORD_CHECK,
}


def _assert_helper_user(user):
    if not getattr(user, "is_helper", False):
        raise ValidationError("Only helper users can manage verification documents.")


def _assert_staff_reviewer(user):
    if not user.is_staff:
        raise ValidationError("Only staff users can review verification documents.")


def _get_helper_profile_for_user(user):
    profile = HelperProfile.objects.filter(user=user).first()
    if not profile:
        raise ValidationError("Helper profile not found.")
    return profile


def document_status_to_trust_signal_status(document_status):
    if document_status in (
        WorkerVerificationDocument.Status.UPLOADED,
        WorkerVerificationDocument.Status.PENDING_REVIEW,
    ):
        return HelperTrustSignal.SignalStatus.PENDING_REVIEW
    if document_status == WorkerVerificationDocument.Status.APPROVED:
        return HelperTrustSignal.SignalStatus.APPROVED
    if document_status == WorkerVerificationDocument.Status.REJECTED:
        return HelperTrustSignal.SignalStatus.REJECTED
    return HelperTrustSignal.SignalStatus.NOT_PROVIDED


def sync_trust_signal_for_document_type(helper_profile, document_type):
    signal_type = DOCUMENT_TYPE_TO_SIGNAL[document_type]
    current = (
        WorkerVerificationDocument.objects.filter(
            helper=helper_profile,
            document_type=document_type,
            is_current=True,
        )
        .order_by("-uploaded_at")
        .first()
    )
    if not current:
        status = HelperTrustSignal.SignalStatus.NOT_PROVIDED
        notes = ""
    else:
        status = document_status_to_trust_signal_status(current.status)
        notes = current.review_note if current.status == WorkerVerificationDocument.Status.REJECTED else ""

    trust_signal, _ = HelperTrustSignal.objects.update_or_create(
        helper=helper_profile,
        signal_type=signal_type,
        defaults={"status": status, "notes": notes},
    )
    return trust_signal


def sync_verification_trust_signals(helper_profile):
    for document_type in DOCUMENT_TYPE_TO_SIGNAL:
        sync_trust_signal_for_document_type(helper_profile, document_type)
    update_helper_trust_status_from_documents(helper_profile)
    return helper_profile


def update_helper_trust_status_from_documents(helper_profile):
    from helpers.selectors.verification_selectors import build_worker_verification_summary

    summary = build_worker_verification_summary(helper_profile)
    if summary["key"] == "verified":
        helper_profile.trust_status = HelperProfile.TrustStatus.VERIFIED
        helper_profile.is_verified = True
    elif summary["key"] in {"pending", "partial"}:
        helper_profile.trust_status = HelperProfile.TrustStatus.READY_FOR_REVIEW
    else:
        if helper_profile.trust_status == HelperProfile.TrustStatus.VERIFIED:
            helper_profile.trust_status = HelperProfile.TrustStatus.READY_FOR_REVIEW
        helper_profile.is_verified = False
    helper_profile.save(update_fields=["trust_status", "is_verified", "updated_at"])


@transaction.atomic
def upload_worker_verification_document(*, user, document_type, uploaded_file):
    _assert_helper_user(user)
    helper_profile = _get_helper_profile_for_user(user)

    if document_type not in WorkerVerificationDocument.DocumentType.values:
        raise ValidationError("Invalid document type.")

    WorkerVerificationDocument.objects.filter(
        helper=helper_profile,
        document_type=document_type,
        is_current=True,
    ).update(is_current=False)

    document = WorkerVerificationDocument.objects.create(
        helper=helper_profile,
        document_type=document_type,
        file=uploaded_file,
        status=WorkerVerificationDocument.Status.UPLOADED,
        is_current=True,
    )
    sync_trust_signal_for_document_type(helper_profile, document_type)
    update_helper_trust_status_from_documents(helper_profile)
    return document


@transaction.atomic
def review_worker_verification_document(*, document, reviewer, status, review_note=""):
    _assert_staff_reviewer(reviewer)

    if status not in (
        WorkerVerificationDocument.Status.PENDING_REVIEW,
        WorkerVerificationDocument.Status.APPROVED,
        WorkerVerificationDocument.Status.REJECTED,
    ):
        raise ValidationError("Invalid review status.")

    document.status = status
    document.review_note = (review_note or "").strip()[:255]
    document.reviewed_by = reviewer
    document.reviewed_at = timezone.now()
    document.save(update_fields=["status", "review_note", "reviewed_by", "reviewed_at", "updated_at"])

    sync_trust_signal_for_document_type(document.helper, document.document_type)
    update_helper_trust_status_from_documents(document.helper)
    return document
