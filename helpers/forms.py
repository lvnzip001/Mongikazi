from django import forms

from locations.form_fields import (
    apply_locality_fallback_initial,
    bind_locality_fields,
    clean_locality_pair,
    locality_autocomplete_widget,
)
from website.profile_photos import profile_photo_widget, validate_profile_photo

from .models import HelperAvailability, HelperProfile, HelperSkill


class HelperProfileForm(forms.ModelForm):
    location_query = forms.CharField(
        label="Location",
        widget=locality_autocomplete_widget("location_locality_id"),
    )
    location_locality_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    work_area_query = forms.CharField(
        label="Preferred work area",
        widget=locality_autocomplete_widget("work_area_locality_id"),
    )
    work_area_locality_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = HelperProfile
        fields = (
            "display_name",
            "profile_photo",
            "bio",
            "years_experience",
            "availability_summary",
            "is_active",
        )
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Display name"}),
            "profile_photo": profile_photo_widget(),
            "bio": forms.Textarea(attrs={"class": "mk-input", "rows": 4, "placeholder": "Profile bio"}),
            "years_experience": forms.NumberInput(attrs={"class": "mk-input", "min": 0}),
            "availability_summary": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Availability summary"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bind_locality_fields(
            self,
            query_field="location_query",
            id_field="location_locality_id",
            instance=self.instance,
            text_attr="location",
            fk_attr="location_locality",
        )
        bind_locality_fields(
            self,
            query_field="work_area_query",
            id_field="work_area_locality_id",
            instance=self.instance,
            text_attr="preferred_work_area",
            fk_attr="preferred_work_area_locality",
        )
        apply_locality_fallback_initial(
            self,
            query_field="work_area_query",
            id_field="work_area_locality_id",
            source_locality=self.instance.location_locality,
            source_text=self.instance.location,
        )

    def clean(self):
        cleaned = super().clean()
        location = clean_locality_pair(
            cleaned,
            query_field="location_query",
            id_field="location_locality_id",
            field_label="location",
            fallback_locality=self.instance.location_locality,
            fallback_text=self.instance.location,
        )
        work_area = clean_locality_pair(
            cleaned,
            query_field="work_area_query",
            id_field="work_area_locality_id",
            field_label="work area",
            fallback_locality=self.instance.location_locality,
            fallback_text=self.instance.location,
        )
        cleaned["location"] = location.display_label
        cleaned["location_locality"] = location
        cleaned["preferred_work_area"] = work_area.display_label
        cleaned["preferred_work_area_locality"] = work_area
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.location = self.cleaned_data["location"]
        instance.location_locality = self.cleaned_data["location_locality"]
        instance.preferred_work_area = self.cleaned_data["preferred_work_area"]
        instance.preferred_work_area_locality = self.cleaned_data["preferred_work_area_locality"]
        if commit:
            instance.save()
        return instance

    def clean_profile_photo(self):
        upload = self.cleaned_data.get("profile_photo")
        if upload:
            validate_profile_photo(upload)
        return upload

    def clean_years_experience(self):
        years = self.cleaned_data.get("years_experience")
        if years is None:
            return 0
        if years < 0:
            raise forms.ValidationError("Years of experience cannot be negative.")
        return years


class HelperSkillForm(forms.ModelForm):
    class Meta:
        model = HelperSkill
        fields = ("category", "years_experience", "skill_note", "is_primary")
        widgets = {
            "category": forms.Select(attrs={"class": "mk-input"}),
            "years_experience": forms.NumberInput(attrs={"class": "mk-input", "min": 0}),
            "skill_note": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Skill note (optional)"}),
        }

    def clean_years_experience(self):
        years = self.cleaned_data.get("years_experience")
        if years is None:
            return 0
        if years < 0:
            raise forms.ValidationError("Years of experience cannot be negative.")
        return years


class HelperAvailabilityForm(forms.ModelForm):
    class Meta:
        model = HelperAvailability
        fields = ("day_of_week", "start_time", "end_time", "is_available")
        widgets = {
            "day_of_week": forms.Select(attrs={"class": "mk-input"}),
            "start_time": forms.TimeInput(attrs={"class": "mk-input", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "mk-input", "type": "time"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned


class WorkerVerificationUploadForm(forms.Form):
    document_type = forms.ChoiceField(
        choices=[],
        widget=forms.HiddenInput(),
    )
    file = forms.FileField(
        label="Document file",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "mk-input",
                "accept": ".pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/*",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        from helpers.models import WorkerVerificationDocument

        super().__init__(*args, **kwargs)
        self.fields["document_type"].choices = WorkerVerificationDocument.DocumentType.choices

    def clean_file(self):
        from helpers.verification_documents import validate_verification_document

        uploaded = self.cleaned_data.get("file")
        validate_verification_document(uploaded)
        return uploaded
