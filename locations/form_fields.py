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
    from .models import Locality

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
