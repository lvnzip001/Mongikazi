from django import forms

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
    class Meta:
        model = EmployerProfile
        fields = (
            "display_name",
            "employer_type",
            "primary_location_label",
            "primary_area",
            "contact_number",
            "preferred_contact_method",
            "is_active",
        )
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Employer display name"}),
            "employer_type": forms.Select(attrs={"class": "mk-input"}),
            "primary_location_label": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Home, Office, Apartment"}),
            "primary_area": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Suburb or area"}),
            "contact_number": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Primary contact number"}),
            "preferred_contact_method": forms.Select(attrs={"class": "mk-input"}),
        }


class EmployerLocationForm(EmployerRoleValidationMixin, forms.ModelForm):
    class Meta:
        model = EmployerLocation
        fields = (
            "label",
            "address_line_1",
            "address_line_2",
            "suburb",
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
            "suburb": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Suburb"}),
            "city": forms.TextInput(attrs={"class": "mk-input", "placeholder": "City"}),
            "province": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Province"}),
            "postal_code": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Postal code"}),
            "notes_for_helper": forms.Textarea(attrs={"class": "mk-input", "rows": 3, "placeholder": "Optional access notes"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["address_line_1", "suburb", "city", "province"]:
            self.fields[field].required = True


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