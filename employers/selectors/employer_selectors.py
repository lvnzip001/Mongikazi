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