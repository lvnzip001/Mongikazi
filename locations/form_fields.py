from django import forms

from .selectors import get_locality_by_id, resolve_locality_from_stored_text

# Stable path — do not use reverse() at import time (avoids circular URL loading).
LOCALITY_AUTOCOMPLETE_URL = "/locations/autocomplete/"


def locality_autocomplete_widget(hidden_field_name):
    return LocalityAutocompleteWidget(
        hidden_input_id=f"id_{hidden_field_name}",
        autocomplete_url=LOCALITY_AUTOCOMPLETE_URL,
    )


class LocalityAutocompleteWidget(forms.TextInput):
    def __init__(self, *, hidden_input_id="", autocomplete_url="", **kwargs):
        attrs = kwargs.pop("attrs", {})
        attrs.setdefault("class", "mk-input")
        attrs.setdefault("autocomplete", "off")
        attrs.setdefault("data-locality-autocomplete", "true")
        if hidden_input_id:
            attrs["data-locality-hidden-id"] = hidden_input_id
        if autocomplete_url:
            attrs["data-locality-url"] = autocomplete_url
        super().__init__(attrs=attrs)


def bind_locality_fields(form, *, query_field, id_field, instance=None, text_attr=None, fk_attr=None):
    """Set initial values for locality autocomplete fields on a form instance."""
    locality = None
    if instance and fk_attr:
        locality = getattr(instance, fk_attr, None)
    if locality:
        form.initial[id_field] = locality.pk
        form.initial[query_field] = locality.display_label
        return
    if instance and text_attr:
        stored = (getattr(instance, text_attr, None) or "").strip()
        if not stored:
            return
        locality = resolve_locality_from_stored_text(stored)
        if locality:
            form.initial[id_field] = locality.pk
            form.initial[query_field] = locality.display_label
        else:
            form.initial[query_field] = stored


def resolve_locality_from_form(cleaned_id, *, field_label="location"):
    locality = get_locality_by_id(cleaned_id)
    if not locality:
        raise forms.ValidationError(f"Select a valid {field_label} from the suggestions.")
    return locality


def apply_locality_fallback_initial(
    form,
    *,
    query_field,
    id_field,
    source_locality=None,
    source_text="",
):
    """Prefill hidden locality id when only a label exists (e.g. carried from a prior step)."""
    if form.is_bound or form.initial.get(id_field):
        return
    if source_locality:
        form.initial[id_field] = source_locality.pk
        form.initial[query_field] = source_locality.display_label
        return
    text = (source_text or "").strip()
    if not text:
        return
    locality = resolve_locality_from_stored_text(text)
    if locality:
        form.initial[id_field] = locality.pk
        form.initial[query_field] = locality.display_label
    else:
        form.initial[query_field] = text


def clean_locality_pair(
    cleaned,
    *,
    query_field,
    id_field,
    field_label,
    fallback_locality=None,
    fallback_text="",
):
    """Resolve hidden locality id from query text and optional fallback source."""
    locality_id = cleaned.get(id_field)
    query = (cleaned.get(query_field) or "").strip()

    if not locality_id and fallback_locality:
        labels = {fallback_locality.display_label}
        if fallback_text:
            labels.add(fallback_text.strip())
        if query in {label for label in labels if label}:
            locality_id = fallback_locality.pk

    if not locality_id and query:
        match = resolve_locality_from_stored_text(query)
        if match:
            locality_id = match.pk

    locality = resolve_locality_from_form(locality_id, field_label=field_label)
    cleaned[id_field] = locality.pk
    return locality
