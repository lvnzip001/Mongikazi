from helpers.models import HelperAvailability, HelperProfile, HelperSkill, HelperTrustSignal
from website.profile_photos import has_profile_photo


def sync_profile_photo_trust_signal(helper_profile):
    status = (
        HelperTrustSignal.SignalStatus.READY
        if has_profile_photo(helper_profile)
        else HelperTrustSignal.SignalStatus.NOT_PROVIDED
    )
    HelperTrustSignal.objects.update_or_create(
        helper=helper_profile,
        signal_type=HelperTrustSignal.SignalType.PROFILE_PHOTO,
        defaults={"status": status},
    )


def calculate_helper_profile_completion(helper_profile):
    sync_profile_photo_trust_signal(helper_profile)

    percent = 0

    basic_complete = all(
        [
            bool(helper_profile.display_name),
            bool(helper_profile.location),
            bool(helper_profile.bio),
            helper_profile.years_experience >= 0,
        ]
    )
    if basic_complete:
        percent += 30

    if HelperSkill.objects.filter(helper=helper_profile).exists():
        percent += 20

    has_availability_rows = HelperAvailability.objects.filter(helper=helper_profile, is_available=True).exists()
    if helper_profile.availability_summary or has_availability_rows:
        percent += 15

    signal_count = HelperTrustSignal.objects.filter(helper=helper_profile).count()
    if signal_count >= 3:
        percent += 20

    if has_profile_photo(helper_profile):
        percent += 15

    percent = min(percent, 100)
    helper_profile.profile_completion_percent = percent
    helper_profile.is_profile_complete = percent >= 70

    if helper_profile.is_verified:
        helper_profile.trust_status = HelperProfile.TrustStatus.VERIFIED
    elif helper_profile.trust_status == HelperProfile.TrustStatus.SUSPENDED:
        pass
    elif helper_profile.trust_status not in (
        HelperProfile.TrustStatus.VERIFIED,
        HelperProfile.TrustStatus.READY_FOR_REVIEW,
    ):
        if helper_profile.profile_completion_percent >= 70:
            helper_profile.trust_status = HelperProfile.TrustStatus.READY_FOR_REVIEW
        elif helper_profile.profile_completion_percent > 0:
            helper_profile.trust_status = HelperProfile.TrustStatus.PROFILE_STARTED
        else:
            helper_profile.trust_status = HelperProfile.TrustStatus.NEW

    helper_profile.save(update_fields=["profile_completion_percent", "is_profile_complete", "trust_status", "updated_at"])
    return helper_profile.profile_completion_percent
