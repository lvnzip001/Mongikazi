from django.forms import ValidationError
from django.utils.text import slugify

from onboarding.models import HelperOnboardingProfile

from helpers.models import HelperProfile, HelperSkill, HelperTrustSignal, ServiceCategory
from helpers.services.profile_completion_service import calculate_helper_profile_completion


DEFAULT_SERVICE_CATEGORIES = [
    ("Cleaning", "General home and apartment cleaning"),
    ("Laundry", "Laundry washing and ironing"),
    ("Cooking", "Meal preparation and home cooking"),
    ("Childcare", "Childcare support"),
    ("Office cleaning", "Office and workspace cleaning"),
]


def ensure_default_service_categories():
    categories = []
    for index, (name, description) in enumerate(DEFAULT_SERVICE_CATEGORIES, start=1):
        category, _ = ServiceCategory.objects.get_or_create(
            slug=slugify(name),
            defaults={"name": name, "description": description, "sort_order": index, "is_active": True},
        )
        categories.append(category)
    return categories


def _assert_helper_user(user):
    if not getattr(user, "is_helper", False):
        raise ValidationError("Only helper users can use helper onboarding handoff.")


def create_or_update_helper_profile_from_onboarding(user):
    _assert_helper_user(user)
    onboarding_profile = HelperOnboardingProfile.objects.filter(user=user).first()
    if not onboarding_profile:
        raise ValidationError("Helper onboarding profile not found.")

    ensure_default_service_categories()

    display_name = onboarding_profile.display_name.strip() if onboarding_profile.display_name else ""
    if not display_name:
        display_name = " ".join(part for part in [user.first_name, user.last_name] if part).strip() or user.username

    helper_profile, _ = HelperProfile.objects.get_or_create(user=user)
    helper_profile.display_name = display_name
    helper_profile.location = onboarding_profile.location
    helper_profile.location_locality = onboarding_profile.location_locality
    helper_profile.years_experience = onboarding_profile.years_experience or 0
    helper_profile.bio = onboarding_profile.bio
    helper_profile.preferred_work_area = onboarding_profile.preferred_work_area
    helper_profile.preferred_work_area_locality = onboarding_profile.preferred_work_area_locality
    helper_profile.availability_summary = onboarding_profile.availability_summary
    helper_profile.save()

    sync_helper_skills_from_onboarding(user)
    sync_helper_trust_signals_from_onboarding(user)
    calculate_helper_profile_completion(helper_profile)

    return helper_profile


def sync_helper_skills_from_onboarding(user):
    _assert_helper_user(user)
    onboarding_profile = HelperOnboardingProfile.objects.filter(user=user).first()
    if not onboarding_profile:
        return []

    helper_profile, _ = HelperProfile.objects.get_or_create(user=user)
    ensure_default_service_categories()

    selected_values = [value for value in onboarding_profile.selected_categories.split(",") if value]
    selected_slugs = {slugify(value.replace("_", " ")) for value in selected_values}
    kept_ids = set()

    for slug in selected_slugs:
        category = ServiceCategory.objects.filter(slug=slug).first()
        if not category:
            category = ServiceCategory.objects.create(name=slug.replace("-", " ").title(), slug=slug, is_active=True)
        skill, _ = HelperSkill.objects.get_or_create(
            helper=helper_profile,
            category=category,
            defaults={"years_experience": helper_profile.years_experience},
        )
        kept_ids.add(skill.id)

    HelperSkill.objects.filter(helper=helper_profile).exclude(id__in=kept_ids).delete()
    return list(HelperSkill.objects.filter(helper=helper_profile))


def sync_helper_trust_signals_from_onboarding(user):
    _assert_helper_user(user)
    onboarding_profile = HelperOnboardingProfile.objects.filter(user=user).first()
    if not onboarding_profile:
        return []

    helper_profile, _ = HelperProfile.objects.get_or_create(user=user)
    map_status = lambda flag: HelperTrustSignal.SignalStatus.READY if flag else HelperTrustSignal.SignalStatus.NOT_PROVIDED

    signal_values = {
        HelperTrustSignal.SignalType.ID_DOCUMENT: map_status(onboarding_profile.has_id_document_ready),
        HelperTrustSignal.SignalType.CRIMINAL_RECORD_CHECK: map_status(onboarding_profile.has_criminal_check_ready),
        HelperTrustSignal.SignalType.REFERENCES: map_status(onboarding_profile.has_references),
        HelperTrustSignal.SignalType.EXPERIENCE_CAPTURED: (
            HelperTrustSignal.SignalStatus.READY if helper_profile.years_experience > 0 else HelperTrustSignal.SignalStatus.NOT_PROVIDED
        ),
        HelperTrustSignal.SignalType.PROFILE_PHOTO: (
            HelperTrustSignal.SignalStatus.READY if helper_profile.profile_photo else HelperTrustSignal.SignalStatus.NOT_PROVIDED
        ),
    }

    records = []
    for signal_type, status in signal_values.items():
        trust_signal, _ = HelperTrustSignal.objects.update_or_create(
            helper=helper_profile,
            signal_type=signal_type,
            defaults={"status": status},
        )
        records.append(trust_signal)
    return records
