from django.db.models import Q

from .models import Locality


def search_localities(query, *, limit=12):
    term = (query or "").strip()
    if len(term) < 2:
        return Locality.objects.none()

    return (
        Locality.objects.filter(is_active=True)
        .filter(
            Q(name__icontains=term)
            | Q(search_text__icontains=term.lower())
            | Q(municipality__icontains=term)
            | Q(province__icontains=term)
        )
        .order_by("sort_order", "name")[:limit]
    )


def get_locality_by_id(locality_id):
    if not locality_id:
        return None
    try:
        return Locality.objects.get(pk=locality_id, is_active=True)
    except Locality.DoesNotExist:
        return None


def resolve_locality_from_stored_text(stored):
    """Match a saved label like 'East London, Eastern Cape' or plain 'Benoni'."""
    text = (stored or "").strip()
    if not text:
        return None

    locality = Locality.objects.filter(is_active=True, name__iexact=text).first()
    if locality:
        return locality

    if "," in text:
        name, province = (part.strip() for part in text.split(",", 1))
        if name and province:
            locality = Locality.objects.filter(
                is_active=True,
                name__iexact=name,
                province__iexact=province,
            ).first()
            if locality:
                return locality

    return (
        Locality.objects.filter(is_active=True)
        .filter(
            Q(name__iexact=text)
            | Q(search_text__icontains=text.lower())
        )
        .order_by("sort_order", "name")
        .first()
    )
