from django import forms

from locations.form_fields import (
    apply_locality_fallback_initial,
    bind_locality_fields,
    clean_locality_pair,
    locality_autocomplete_widget,
)
from website.profile_photos import profile_photo_widget, validate_profile_photo

from .models import EmployerLocation, EmployerProfile, EmployerServicePreference


class EmployerRoleValidationMixin:
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if self.user and not getattr(self.user, "is_employer", False):
            raise forms.ValidationError("Only employer users can update employer profile data.")
        return cleaned


class EmployerProfileForm(EmployerRoleValidationMixin, forms.ModelForm):
    primary_area_query = forms.CharField(
        label="Primary area",
        widget=locality_autocomplete_widget("primary_area_locality_id"),
    )
    primary_area_locality_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = EmployerProfile
        fields = (
            "display_name",
            "profile_photo",
            "employer_type",
            "primary_location_label",
            "contact_number",
            "preferred_contact_method",
            "is_active",
        )
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Employer display name"}),
            "profile_photo": profile_photo_widget(),
            "employer_type": forms.Select(attrs={"class": "mk-input"}),
            "primary_location_label": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Home, Office, Apartment"}),
            "contact_number": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Primary contact number"}),
            "preferred_contact_method": forms.Select(attrs={"class": "mk-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bind_locality_fields(
            self,
            query_field="primary_area_query",
            id_field="primary_area_locality_id",
            instance=self.instance,
            text_attr="primary_area",
            fk_attr="primary_area_locality",
        )

    def clean_profile_photo(self):
        upload = self.cleaned_data.get("profile_photo")
        if upload:
            validate_profile_photo(upload)
        return upload

    def clean(self):
        cleaned = super().clean()
        locality = clean_locality_pair(
            cleaned,
            query_field="primary_area_query",
            id_field="primary_area_locality_id",
            field_label="area",
            fallback_locality=self.instance.primary_area_locality,
            fallback_text=self.instance.primary_area,
        )
        cleaned["primary_area"] = locality.display_label
        cleaned["primary_area_locality"] = locality
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.primary_area = self.cleaned_data["primary_area"]
        instance.primary_area_locality = self.cleaned_data["primary_area_locality"]
        if commit:
            instance.save()
        return instance


class EmployerLocationForm(EmployerRoleValidationMixin, forms.ModelForm):
    suburb_query = forms.CharField(
        label="Suburb / area",
        widget=locality_autocomplete_widget("suburb_locality_id"),
    )
    suburb_locality_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = EmployerLocation
        fields = (
            "label",
            "address_line_1",
            "address_line_2",
            "city",
            "province",
            "postal_code",
            "notes_for_helper",
            "is_primary",
        )
        widgets = {
            "label": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Home, Office, Apartment"}),
            "address_line_1": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Street address"}),
            "address_line_2": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Unit, complex, optional"}),
            "city": forms.TextInput(attrs={"class": "mk-input", "placeholder": "City"}),
            "province": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Province"}),
            "postal_code": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Postal code"}),
            "notes_for_helper": forms.Textarea(attrs={"class": "mk-input", "rows": 3, "placeholder": "Optional access notes"}),
        }

    def __init__(self, *args, **kwargs):
        self.employer_profile = kwargs.pop("employer_profile", None)
        super().__init__(*args, **kwargs)
        for field in ["address_line_1", "city", "province"]:
            self.fields[field].required = True
        bind_locality_fields(
            self,
            query_field="suburb_query",
            id_field="suburb_locality_id",
            instance=self.instance,
            text_attr="suburb",
            fk_attr="locality",
        )
        employer = self.employer_profile or getattr(self.instance, "employer", None)
        if employer and not self.initial.get("suburb_locality_id"):
            apply_locality_fallback_initial(
                self,
                query_field="suburb_query",
                id_field="suburb_locality_id",
                source_locality=employer.primary_area_locality,
                source_text=employer.primary_area,
            )

    def clean(self):
        cleaned = super().clean()
        employer = self.employer_profile or getattr(self.instance, "employer", None)
        locality = clean_locality_pair(
            cleaned,
            query_field="suburb_query",
            id_field="suburb_locality_id",
            field_label="suburb",
            fallback_locality=employer.primary_area_locality if employer else None,
            fallback_text=employer.primary_area if employer else "",
        )
        cleaned["suburb"] = locality.name
        cleaned["locality"] = locality
        if not cleaned.get("city"):
            cleaned["city"] = locality.municipality or locality.name
        if not cleaned.get("province"):
            cleaned["province"] = locality.province
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.suburb = self.cleaned_data["suburb"]
        instance.locality = self.cleaned_data["locality"]
        if commit:
            instance.save()
        return instance


class EmployerServicePreferenceForm(EmployerRoleValidationMixin, forms.ModelForm):
    class Meta:
        model = EmployerServicePreference
        fields = (
            "service_type",
            "service_frequency",
            "preferred_day",
            "preferred_time",
            "estimated_duration_hours",
            "special_instructions",
        )
        widgets = {
            "service_type": forms.Select(attrs={"class": "mk-input"}),
            "service_frequency": forms.Select(attrs={"class": "mk-input"}),
            "preferred_day": forms.Select(attrs={"class": "mk-input"}),
            "preferred_time": forms.TimeInput(attrs={"class": "mk-input", "type": "time"}),
            "estimated_duration_hours": forms.NumberInput(attrs={"class": "mk-input", "min": 1}),
            "special_instructions": forms.Textarea(attrs={"class": "mk-input", "rows": 4, "placeholder": "Any special instructions"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_type"].required = True
        self.fields["service_frequency"].required = True

    def clean_estimated_duration_hours(self):
        duration = self.cleaned_data.get("estimated_duration_hours")
        if duration is None or duration <= 0:
            raise forms.ValidationError("Estimated duration must be greater than zero.")
        return duration
