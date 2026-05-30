from employers.models import EmployerLocation, EmployerProfile, EmployerServicePreference, EmployerTrustSignal


def get_employer_profile_for_user(user):
    return EmployerProfile.objects.filter(user=user).first()


def get_active_employer_profiles():
    return EmployerProfile.objects.filter(is_active=True).select_related("user")


def get_employer_locations(employer_profile):
    return EmployerLocation.objects.filter(employer=employer_profile, is_active=True)


def get_primary_employer_location(employer_profile):
    return EmployerLocation.objects.filter(employer=employer_profile, is_primary=True, is_active=True).first()


def get_employer_service_preferences(employer_profile):
    return EmployerServicePreference.objects.filter(employer=employer_profile)


def get_employer_trust_signals(employer_profile):
    return EmployerTrustSignal.objects.filter(employer=employer_profile)


def get_employer_profile_preview_context(employer_profile):
    preference = get_employer_service_preferences(employer_profile).first()
    location = get_primary_employer_location(employer_profile)
    trust_signals = list(get_employer_trust_signals(employer_profile))
    return {
        "employer": employer_profile,
        "preference": preference,
        "location": location,
        "trust_signals": trust_signals,
    }


def _employer_trust_signal_status(trust_signals_by_type, signal_type):
    return trust_signals_by_type.get(signal_type, EmployerTrustSignal.SignalStatus.NOT_PROVIDED)


def build_worker_safe_employer_card(employer_profile, booking=None):
    """Privacy-safe employer snapshot for workers reviewing a job before applying."""
    if not employer_profile:
        return {
            "display_name": "Employer",
            "employer_type": "",
            "service_area": "",
            "completed_bookings": 0,
            "average_rating": None,
            "profile_completion_percent": 0,
            "preferred_service": "",
            "service_frequency": "",
            "badges": [],
            "has_profile": False,
        }

    trust_signals_by_type = {
        signal.signal_type: signal.status for signal in get_employer_trust_signals(employer_profile)
    }
    preference = get_employer_service_preferences(employer_profile).first()

    if booking and getattr(booking, "employer_location", None):
        service_area = booking.employer_location.service_area_display()
    elif employer_profile.primary_area:
        service_area = employer_profile.primary_area
    else:
        service_area = ""

    badges = []
    if employer_profile.is_verified:
        badges.append({"label": "Verified employer", "variant": "success"})

    phone_status = _employer_trust_signal_status(
        trust_signals_by_type, EmployerTrustSignal.SignalType.PHONE_VERIFIED
    )
    if phone_status in (EmployerTrustSignal.SignalStatus.READY, EmployerTrustSignal.SignalStatus.APPROVED):
        badges.append({"label": "Phone verified", "variant": "success"})

    location_status = _employer_trust_signal_status(
        trust_signals_by_type, EmployerTrustSignal.SignalType.LOCATION_CAPTURED
    )
    if location_status in (EmployerTrustSignal.SignalStatus.READY, EmployerTrustSignal.SignalStatus.APPROVED):
        badges.append({"label": "Location confirmed", "variant": "neutral"})

    if employer_profile.completed_bookings > 0:
        badges.append({"label": "Has booking history", "variant": "neutral"})

    if employer_profile.is_profile_complete:
        badges.append({"label": "Profile complete", "variant": "neutral"})

    has_profile = bool(
        employer_profile.display_name
        or employer_profile.is_profile_complete
        or employer_profile.profile_photo
        or employer_profile.primary_area
    )

    return {
        "display_name": employer_profile.display_name or "Employer",
        "employer_type": employer_profile.get_employer_type_display(),
        "service_area": service_area,
        "completed_bookings": employer_profile.completed_bookings,
        "average_rating": employer_profile.average_rating,
        "profile_completion_percent": employer_profile.profile_completion_percent,
        "preferred_service": preference.get_service_type_display() if preference and preference.service_type else "",
        "service_frequency": (
            preference.get_service_frequency_display() if preference and preference.service_frequency else ""
        ),
        "badges": badges,
        "has_profile": has_profile,
    }