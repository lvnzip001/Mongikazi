"""Validation helpers for worker verification document uploads."""

from __future__ import annotations

import os

from django.core.exceptions import ValidationError

MAX_VERIFICATION_DOCUMENT_BYTES = 10 * 1024 * 1024
ALLOWED_VERIFICATION_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}
ALLOWED_VERIFICATION_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}


def validate_verification_document(upload):
    if not upload:
        raise ValidationError("Please choose a file to upload.")
    if upload.size > MAX_VERIFICATION_DOCUMENT_BYTES:
        raise ValidationError("Document must be 10 MB or smaller.")
    content_type = (getattr(upload, "content_type", None) or "").lower()
    if content_type and content_type not in ALLOWED_VERIFICATION_CONTENT_TYPES:
        raise ValidationError("Please upload a PDF, JPG, PNG, or WebP file.")
    extension = os.path.splitext(upload.name or "")[1].lower()
    if extension and extension not in ALLOWED_VERIFICATION_EXTENSIONS:
        raise ValidationError("Please upload a PDF, JPG, PNG, or WebP file.")
