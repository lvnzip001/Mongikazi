"""Shared profile photo validation and display helpers."""

from __future__ import annotations

import os

from django import forms
from django.core.exceptions import ValidationError

MAX_PROFILE_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_PROFILE_PHOTO_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}
ALLOWED_PROFILE_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def validate_profile_photo(upload):
    if not upload:
        return
    if upload.size > MAX_PROFILE_PHOTO_BYTES:
        raise ValidationError("Profile photo must be 5 MB or smaller.")
    content_type = (getattr(upload, "content_type", None) or "").lower()
    if content_type and content_type not in ALLOWED_PROFILE_PHOTO_TYPES:
        raise ValidationError("Please upload a JPG, PNG, or WebP image.")
    extension = os.path.splitext(upload.name or "")[1].lower()
    if extension and extension not in ALLOWED_PROFILE_PHOTO_EXTENSIONS:
        raise ValidationError("Please upload a JPG, PNG, or WebP image.")


def profile_photo_form_field(*, required=False, label="Profile photo"):
    return forms.ImageField(
        label=label,
        required=required,
        validators=[validate_profile_photo],
        widget=forms.ClearableFileInput(
            attrs={
                "class": "mk-input mk-profile-photo-input",
                "accept": "image/*",
                "capture": "user",
            }
        ),
    )


def profile_photo_widget():
    return forms.ClearableFileInput(
        attrs={
            "class": "mk-input mk-profile-photo-input",
            "accept": "image/*",
            "capture": "user",
        }
    )


def _photo_file(subject):
    if subject is None:
        return None
    photo = getattr(subject, "profile_photo", None)
    if photo and getattr(photo, "name", ""):
        return photo
    user = getattr(subject, "user", None)
    if user:
        user_photo = getattr(user, "profile_photo", None)
        if user_photo and getattr(user_photo, "name", ""):
            return user_photo
    return None


def profile_photo_url(subject):
    photo = _photo_file(subject)
    if not photo:
        return ""
    try:
        return photo.url
    except (ValueError, AttributeError):
        return ""


def has_profile_photo(subject):
    return _photo_file(subject) is not None


def profile_display_name(subject):
    if subject is None:
        return "Member"
    name = (getattr(subject, "display_name", None) or "").strip()
    if name:
        return name
    user = getattr(subject, "user", None)
    if user:
        full = (user.get_full_name() or "").strip()
        if full:
            return full
        return user.username or "Member"
    return "Member"


def profile_initials(subject):
    name = profile_display_name(subject)
    parts = [part for part in name.replace(".", " ").split() if part]
    if not parts:
        return "M"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[1][0]}".upper()


def profile_subtitle(subject):
    if subject is None:
        return ""
    for attr in ("location", "primary_area", "bio"):
        value = (getattr(subject, attr, None) or "").strip()
        if value:
            return value[:120]
    return ""


def avatar_context(subject, *, size="md", subtitle=""):
    return {
        "photo_url": profile_photo_url(subject),
        "name": profile_display_name(subject),
        "initials": profile_initials(subject),
        "subtitle": subtitle or profile_subtitle(subject),
        "size": size,
    }
