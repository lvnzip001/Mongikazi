from django import forms

from locations.form_fields import (
    apply_locality_fallback_initial,
    bind_locality_fields,
    clean_locality_pair,
    locality_autocomplete_widget,
)

from .models import EmployerOnboardingProfile, HelperOnboardingProfile


class EmployerServiceForm(forms.ModelForm):
    class Meta:
        model = EmployerOnboardingProfile
        fields = ("service_type", "service_frequency")
        widgets = {
            "service_type": forms.Select(attrs={"class": "mk-input"}),
            "service_frequency": forms.Select(attrs={"class": "mk-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_type"].required = True
        self.fields["service_frequency"].required = True


class EmployerLocationForm(forms.ModelForm):
    preferred_location_query = forms.CharField(
        label="Preferred location",
        widget=locality_autocomplete_widget("preferred_location_locality_id"),
    )
    preferred_location_locality_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = EmployerOnboardingProfile
        fields = ("preferred_start_date", "preferred_time", "special_instructions")
        widgets = {
            "preferred_start_date": forms.DateInput(attrs={"class": "mk-input", "type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"class": "mk-input", "type": "time"}),
            "special_instructions": forms.Textarea(
                attrs={"class": "mk-input", "rows": 4, "placeholder": "Any specific instructions"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_start_date"].required = True
        self.fields["preferred_time"].required = True
        bind_locality_fields(
            self,
            query_field="preferred_location_query",
            id_field="preferred_location_locality_id",
            instance=self.instance,
            text_attr="preferred_location",
            fk_attr="preferred_location_locality",
        )

    def clean(self):
        cleaned = super().clean()
        locality = clean_locality_pair(
            cleaned,
            query_field="preferred_location_query",
            id_field="preferred_location_locality_id",
            field_label="location",
            fallback_locality=self.instance.preferred_location_locality,
            fallback_text=self.instance.preferred_location,
        )
        cleaned["preferred_location"] = locality.display_label
        cleaned["preferred_location_locality"] = locality
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.preferred_location = self.cleaned_data["preferred_location"]
        instance.preferred_location_locality = self.cleaned_data["preferred_location_locality"]
        if commit:
            instance.save()
        return instance


class HelperProfileForm(forms.ModelForm):
    location_query = forms.CharField(
        label="Location",
        widget=locality_autocomplete_widget("location_locality_id"),
    )
    location_locality_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = HelperOnboardingProfile
        fields = ("display_name", "years_experience", "bio")
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Display name"}),
            "years_experience": forms.NumberInput(attrs={"class": "mk-input", "min": 0, "max": 60}),
            "bio": forms.Textarea(attrs={"class": "mk-input", "rows": 4, "placeholder": "Short profile summary"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_name"].required = True
        self.fields["years_experience"].required = True
        self.fields["bio"].required = True
        bind_locality_fields(
            self,
            query_field="location_query",
            id_field="location_locality_id",
            instance=self.instance,
            text_attr="location",
            fk_attr="location_locality",
        )

    def clean(self):
        cleaned = super().clean()
        locality = clean_locality_pair(
            cleaned,
            query_field="location_query",
            id_field="location_locality_id",
            field_label="location",
            fallback_text=(self.instance.location or "").strip(),
            fallback_locality=self.instance.location_locality,
        )
        cleaned["location"] = locality.display_label
        cleaned["location_locality"] = locality
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.location = self.cleaned_data["location"]
        instance.location_locality = self.cleaned_data["location_locality"]
        if commit:
            instance.save()
        return instance

    def clean_years_experience(self):
        years = self.cleaned_data.get("years_experience")
        if years is None:
            raise forms.ValidationError("Please provide your years of experience.")
        if years > 60:
            raise forms.ValidationError("Please enter a realistic value for years of experience.")
        return years


class HelperServicesForm(forms.ModelForm):
    selected_categories = forms.MultipleChoiceField(
        label="Service categories",
        choices=HelperOnboardingProfile.ServiceCategory.choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    work_area_query = forms.CharField(
        label="Preferred work area",
        widget=locality_autocomplete_widget("work_area_locality_id"),
    )
    work_area_locality_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = HelperOnboardingProfile
        fields = ("availability_summary",)
        widgets = {
            "availability_summary": forms.TextInput(
                attrs={"class": "mk-input"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["availability_summary"].required = True

        if self.instance and self.instance.selected_categories:
            self.fields["selected_categories"].initial = self.instance.categories_list()

        if not self.is_bound and not (self.instance.availability_summary or "").strip():
            self.initial["availability_summary"] = HelperOnboardingProfile.DEFAULT_AVAILABILITY_SUMMARY

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
        locality = clean_locality_pair(
            cleaned,
            query_field="work_area_query",
            id_field="work_area_locality_id",
            field_label="work area",
            fallback_locality=self.instance.location_locality,
            fallback_text=self.instance.location,
        )
        cleaned["preferred_work_area"] = locality.display_label
        cleaned["preferred_work_area_locality"] = locality
        return cleaned

    def clean_availability_summary(self):
        value = (self.cleaned_data.get("availability_summary") or "").strip()
        if not value:
            return HelperOnboardingProfile.DEFAULT_AVAILABILITY_SUMMARY
        return value

    def clean_selected_categories(self):
        categories = self.cleaned_data.get("selected_categories") or []
        if not categories:
            raise forms.ValidationError("Select at least one category.")
        return categories

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_categories = ",".join(self.cleaned_data["selected_categories"])
        instance.preferred_work_area = self.cleaned_data["preferred_work_area"]
        instance.preferred_work_area_locality = self.cleaned_data["preferred_work_area_locality"]
        if commit:
            instance.save()
        return instance


class HelperTrustForm(forms.ModelForm):
    BOOLEAN_CHOICES = (("", "Choose"), ("True", "Yes"), ("False", "No"))

    has_id_document_ready = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES,
        coerce=lambda value: value == "True",
        empty_value=None,
        widget=forms.Select(attrs={"class": "mk-input"}),
    )
    has_criminal_check_ready = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES,
        coerce=lambda value: value == "True",
        empty_value=None,
        widget=forms.Select(attrs={"class": "mk-input"}),
    )
    has_references = forms.TypedChoiceField(
        choices=BOOLEAN_CHOICES,
        coerce=lambda value: value == "True",
        empty_value=None,
        widget=forms.Select(attrs={"class": "mk-input"}),
    )

    class Meta:
        model = HelperOnboardingProfile
        fields = ("has_id_document_ready", "has_criminal_check_ready", "has_references")
