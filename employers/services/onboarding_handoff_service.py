from django.forms import ValidationError

from onboarding.models import EmployerOnboardingProfile

from employers.models import EmployerLocation, EmployerProfile, EmployerServicePreference, EmployerTrustSignal
from employers.services.profile_completion_service import calculate_employer_profile_completion


def _assert_employer_user(user):
    if not getattr(user, "is_employer", False):
        raise ValidationError("Only employer users can use employer onboarding handoff.")


def _resolve_display_name(user, onboarding_profile):
    display_name = (onboarding_profile.user.get_full_name() or "").strip()
    if display_name:
        return display_name
    return user.first_name or user.username


def create_or_update_employer_profile_from_onboarding(user):
    _assert_employer_user(user)
    onboarding_profile = EmployerOnboardingProfile.objects.filter(user=user).first()
    if not onboarding_profile:
        raise ValidationError("Employer onboarding profile not found.")

    employer_profile, _ = EmployerProfile.objects.get_or_create(user=user)
    employer_profile.display_name = _resolve_display_name(user, onboarding_profile)
    employer_profile.primary_area = onboarding_profile.preferred_location or employer_profile.primary_area
    employer_profile.primary_area_locality = (
        onboarding_profile.preferred_location_locality or employer_profile.primary_area_locality
    )
    employer_profile.primary_location_label = employer_profile.primary_location_label or "Home"
    employer_profile.contact_number = user.phone_number or employer_profile.contact_number
    if not employer_profile.preferred_contact_method:
        employer_profile.preferred_contact_method = EmployerProfile.ContactMethod.APP
    employer_profile.save()

    sync_employer_location_from_onboarding(user)
    sync_employer_service_preferences_from_onboarding(user)
    sync_employer_trust_signals_from_onboarding(user)
    calculate_employer_profile_completion(employer_profile)

    return employer_profile


def sync_employer_location_from_onboarding(user):
    _assert_employer_user(user)
    onboarding_profile = EmployerOnboardingProfile.objects.filter(user=user).first()
    if not onboarding_profile:
        return None

    employer_profile, _ = EmployerProfile.objects.get_or_create(user=user)
    if onboarding_profile.preferred_location:
        employer_profile.primary_area = onboarding_profile.preferred_location
        employer_profile.primary_area_locality = onboarding_profile.preferred_location_locality
        employer_profile.save(update_fields=["primary_area", "primary_area_locality", "updated_at"])

    if not any([onboarding_profile.preferred_location, onboarding_profile.special_instructions, employer_profile.primary_area]):
        return None

    locality = onboarding_profile.preferred_location_locality
    area_label = onboarding_profile.preferred_location or employer_profile.primary_area
    suburb_name = locality.name if locality else area_label
    location = EmployerLocation.objects.filter(employer=employer_profile, is_primary=True).first()
    defaults = {
        "label": employer_profile.primary_location_label or "Home",
        "address_line_1": area_label,
        "suburb": suburb_name,
        "locality": locality,
        "city": (locality.municipality or locality.name) if locality else (location.city if location else ""),
        "province": locality.province if locality else (location.province if location else ""),
        "postal_code": location.postal_code if location else "",
        "notes_for_helper": onboarding_profile.special_instructions,
        "is_primary": True,
        "is_active": True,
    }

    if location:
        for key, value in defaults.items():
            setattr(location, key, value)
        location.save()
    else:
        location = EmployerLocation.objects.create(employer=employer_profile, **defaults)

    EmployerLocation.objects.filter(employer=employer_profile).exclude(pk=location.pk).update(is_primary=False)
    return location


def sync_employer_service_preferences_from_onboarding(user):
    _assert_employer_user(user)
    onboarding_profile = EmployerOnboardingProfile.objects.filter(user=user).first()
    if not onboarding_profile:
        return None

    employer_profile, _ = EmployerProfile.objects.get_or_create(user=user)

    if not any(
        [
            onboarding_profile.service_type,
            onboarding_profile.service_frequency,
            onboarding_profile.preferred_time,
            onboarding_profile.special_instructions,
        ]
    ):
        return None

    preference = EmployerServicePreference.objects.filter(employer=employer_profile).first()
    defaults = {
        "service_type": onboarding_profile.service_type,
        "service_frequency": onboarding_profile.service_frequency,
        "preferred_time": onboarding_profile.preferred_time,
        "special_instructions": onboarding_profile.special_instructions,
    }

    if preference:
        for key, value in defaults.items():
            setattr(preference, key, value)
        preference.save()
    else:
        preference = EmployerServicePreference.objects.create(
            employer=employer_profile,
            estimated_duration_hours=4,
            **defaults,
        )

    EmployerServicePreference.objects.filter(employer=employer_profile).exclude(pk=preference.pk).delete()
    return preference


def sync_employer_trust_signals_from_onboarding(user):
    _assert_employer_user(user)
    employer_profile, _ = EmployerProfile.objects.get_or_create(user=user)

    has_location = EmployerLocation.objects.filter(employer=employer_profile, is_active=True).exists()
    has_service_need = EmployerServicePreference.objects.filter(
        employer=employer_profile,
        service_type__gt="",
        service_frequency__gt="",
    ).exists()

    signal_values = {
        EmployerTrustSignal.SignalType.PHONE_VERIFIED: (
            EmployerTrustSignal.SignalStatus.READY
            if user.phone_number
            else EmployerTrustSignal.SignalStatus.NOT_PROVIDED
        ),
        EmployerTrustSignal.SignalType.LOCATION_CAPTURED: (
            EmployerTrustSignal.SignalStatus.READY
            if has_location
            else EmployerTrustSignal.SignalStatus.NOT_PROVIDED
        ),
        EmployerTrustSignal.SignalType.SERVICE_NEED_CAPTURED: (
            EmployerTrustSignal.SignalStatus.READY
            if has_service_need
            else EmployerTrustSignal.SignalStatus.NOT_PROVIDED
        ),
        EmployerTrustSignal.SignalType.BOOKING_HISTORY: (
            EmployerTrustSignal.SignalStatus.READY
            if employer_profile.completed_bookings > 0
            else EmployerTrustSignal.SignalStatus.NOT_PROVIDED
        ),
        EmployerTrustSignal.SignalType.PAYMENT_READINESS: EmployerTrustSignal.SignalStatus.NOT_PROVIDED,
    }

    rows = []
    for signal_type, status in signal_values.items():
        signal, _ = EmployerTrustSignal.objects.update_or_create(
            employer=employer_profile,
            signal_type=signal_type,
            defaults={"status": status},
        )
        rows.append(signal)
    return rows