from django import template

from bookings.display.status_labels import EMPLOYER, WORKER, get_application_status_display, get_booking_status_display

register = template.Library()


def _audience(context):
    return EMPLOYER if context.get("portal_kind") == "employer" else WORKER


@register.simple_tag(takes_context=True)
def booking_status_label(context, booking):
    label, _ = get_booking_status_display(booking.status, audience=_audience(context))
    return label


@register.simple_tag(takes_context=True)
def booking_status_variant(context, booking):
    _, variant = get_booking_status_display(booking.status, audience=_audience(context))
    return variant


@register.simple_tag(takes_context=True)
def application_status_label(context, application):
    label, _ = get_application_status_display(application.status, audience=_audience(context))
    return label


@register.simple_tag(takes_context=True)
def application_status_variant(context, application):
    _, variant = get_application_status_display(application.status, audience=_audience(context))
    return variant


@register.inclusion_tag("bookings/partials/booking_status_badge.html", takes_context=True)
def booking_status_badge(context, booking):
    label, variant = get_booking_status_display(booking.status, audience=_audience(context))
    return {"label": label, "variant": variant}


@register.inclusion_tag("bookings/partials/booking_status_badge.html", takes_context=True)
def application_status_badge(context, application):
    label, variant = get_application_status_display(application.status, audience=_audience(context))
    return {"label": label, "variant": variant}
