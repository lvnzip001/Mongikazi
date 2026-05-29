from django import template

from website.profile_photos import avatar_context, profile_photo_url as resolve_profile_photo_url

register = template.Library()


@register.inclusion_tag("components/profile_avatar.html")
def profile_avatar(profile, size="md", subtitle=""):
    return avatar_context(profile, size=size, subtitle=subtitle)


@register.filter
def profile_photo_url(subject):
    return resolve_profile_photo_url(subject)
