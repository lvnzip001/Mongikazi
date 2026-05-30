from helpers.models import HelperProfile, HelperTrustSignal, WorkerVerificationDocument
from helpers.selectors.helper_selectors import get_helper_profile_for_user, get_helper_skills, get_helper_trust_signals
from helpers.services.profile_completion_service import sync_profile_photo_trust_signal


VERIFICATION_DOCUMENT_TYPES = (
    WorkerVerificationDocument.DocumentType.ID_DOCUMENT,
    WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK,
)


def get_current_verification_documents(helper_profile):
    if not helper_profile:
        return {doc_type: None for doc_type in VERIFICATION_DOCUMENT_TYPES}

    current_docs = {
        doc.document_type: doc
        for doc in WorkerVerificationDocument.objects.filter(
            helper=helper_profile,
            is_current=True,
            document_type__in=VERIFICATION_DOCUMENT_TYPES,
        )
    }
    return {doc_type: current_docs.get(doc_type) for doc_type in VERIFICATION_DOCUMENT_TYPES}


def build_worker_verification_summary(helper_profile):
    documents = get_current_verification_documents(helper_profile)
    id_doc = documents[WorkerVerificationDocument.DocumentType.ID_DOCUMENT]
    criminal_doc = documents[WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK]

    id_approved = id_doc and id_doc.status == WorkerVerificationDocument.Status.APPROVED
    criminal_approved = criminal_doc and criminal_doc.status == WorkerVerificationDocument.Status.APPROVED

    if id_approved and criminal_approved:
        return {"key": "verified", "label": "Verified"}

    pending_statuses = {
        WorkerVerificationDocument.Status.UPLOADED,
        WorkerVerificationDocument.Status.PENDING_REVIEW,
    }
    has_pending = any(doc and doc.status in pending_statuses for doc in documents.values())
    has_any_upload = any(doc for doc in documents.values())
    has_any_approved = id_approved or criminal_approved

    if has_pending:
        return {"key": "pending", "label": "Verification pending"}
    if has_any_approved or has_any_upload:
        return {"key": "partial", "label": "Partially verified"}
    return {"key": "unverified", "label": "Unverified"}


def _trust_signal_status(helper_profile, signal_type):
    signal = HelperTrustSignal.objects.filter(helper=helper_profile, signal_type=signal_type).first()
    return signal.status if signal else HelperTrustSignal.SignalStatus.NOT_PROVIDED


def build_employer_safe_worker_card(worker_profile):
    if not worker_profile:
        return {
            "display_name": "Worker",
            "location": "",
            "bio_snippet": "",
            "years_experience": 0,
            "service_categories": [],
            "average_rating": None,
            "completed_jobs": 0,
            "badges": [],
        }

    skills = list(get_helper_skills(worker_profile))
    service_categories = [skill.category.name for skill in skills if getattr(skill, "category", None)]
    bio = (worker_profile.bio or "").strip()
    bio_snippet = bio[:160] + ("…" if len(bio) > 160 else "")

    badges = []
    id_status = _trust_signal_status(worker_profile, HelperTrustSignal.SignalType.ID_DOCUMENT)
    criminal_status = _trust_signal_status(worker_profile, HelperTrustSignal.SignalType.CRIMINAL_RECORD_CHECK)

    if id_status == HelperTrustSignal.SignalStatus.APPROVED:
        badges.append({"label": "ID verified", "variant": "success"})
    elif id_status == HelperTrustSignal.SignalStatus.PENDING_REVIEW:
        badges.append({"label": "ID pending review", "variant": "warning"})

    if criminal_status == HelperTrustSignal.SignalStatus.APPROVED:
        badges.append({"label": "Criminal check verified", "variant": "success"})
    elif criminal_status in (
        HelperTrustSignal.SignalStatus.PENDING_REVIEW,
        HelperTrustSignal.SignalStatus.READY,
    ):
        badges.append({"label": "Criminal check pending review", "variant": "warning"})

    if worker_profile.is_profile_complete:
        badges.append({"label": "Profile complete", "variant": "neutral"})

    return {
        "display_name": worker_profile.display_name or "Worker",
        "location": worker_profile.location or worker_profile.preferred_work_area or "",
        "bio_snippet": bio_snippet,
        "years_experience": worker_profile.years_experience,
        "service_categories": service_categories[:6],
        "average_rating": worker_profile.average_rating,
        "completed_jobs": worker_profile.completed_jobs,
        "badges": badges,
    }


def get_worker_verification_page_context(user):
    helper_profile = get_helper_profile_for_user(user)
    if helper_profile:
        sync_profile_photo_trust_signal(helper_profile)
    documents = get_current_verification_documents(helper_profile)
    summary = build_worker_verification_summary(helper_profile)
    trust_signals = list(get_helper_trust_signals(helper_profile)) if helper_profile else []

    non_document_signals = [
        signal
        for signal in trust_signals
        if signal.signal_type
        not in (
            HelperTrustSignal.SignalType.ID_DOCUMENT,
            HelperTrustSignal.SignalType.CRIMINAL_RECORD_CHECK,
        )
    ]

    document_cards = []
    guidance = {
        WorkerVerificationDocument.DocumentType.ID_DOCUMENT: (
            "Upload a clear photo or PDF of your South African ID or passport."
        ),
        WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK: (
            "Upload your criminal record check certificate (PDF or clear photo)."
        ),
    }
    labels = {
        WorkerVerificationDocument.DocumentType.ID_DOCUMENT: "ID document",
        WorkerVerificationDocument.DocumentType.CRIMINAL_RECORD_CHECK: "Criminal record check",
    }

    for doc_type in VERIFICATION_DOCUMENT_TYPES:
        document = documents.get(doc_type)
        if not document:
            status_key = "not_uploaded"
            status_label = "Not uploaded"
        else:
            status_key = document.status.lower()
            status_label = document.get_status_display()
        document_cards.append(
            {
                "document_type": doc_type,
                "label": labels[doc_type],
                "guidance": guidance[doc_type],
                "document": document,
                "status_key": status_key,
                "status_label": status_label,
            }
        )

    return {
        "profile": helper_profile,
        "summary": summary,
        "document_cards": document_cards,
        "non_document_signals": non_document_signals,
    }
