from employers.models import EmployerLocation, EmployerProfile, EmployerServicePreference, EmployerTrustSignal


def calculate_employer_profile_completion(employer_profile):
    percent = 0

    basic_complete = all(
        [
            bool(employer_profile.display_name),
            bool(employer_profile.employer_type),
            bool(employer_profile.primary_area),
        ]
    )
    if basic_complete:
        percent += 25

    has_active_location = EmployerLocation.objects.filter(employer=employer_profile, is_active=True).exists()
    if has_active_location:
        percent += 25

    has_service_pref = EmployerServicePreference.objects.filter(
        employer=employer_profile,
        service_type__gt="",
        service_frequency__gt="",
    ).exists()
    if has_service_pref:
        percent += 25

    trust_signal_count = EmployerTrustSignal.objects.filter(employer=employer_profile).count()
    if trust_signal_count >= 3:
        percent += 15

    if employer_profile.preferred_contact_method and employer_profile.contact_number:
        percent += 10

    percent = min(percent, 100)
    employer_profile.profile_completion_percent = percent
    employer_profile.is_profile_complete = percent >= 70

    if employer_profile.is_verified:
        employer_profile.trust_status = EmployerProfile.TrustStatus.VERIFIED
    elif employer_profile.trust_status == EmployerProfile.TrustStatus.SUSPENDED:
        employer_profile.trust_status = EmployerProfile.TrustStatus.SUSPENDED
    elif percent >= 70:
        employer_profile.trust_status = EmployerProfile.TrustStatus.READY_FOR_BOOKING
    elif percent > 0:
        employer_profile.trust_status = EmployerProfile.TrustStatus.PROFILE_STARTED
    else:
        employer_profile.trust_status = EmployerProfile.TrustStatus.NEW

    employer_profile.save(update_fields=["profile_completion_percent", "is_profile_complete", "trust_status", "updated_at"])
    return employer_profile.profile_completion_percent