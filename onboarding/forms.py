from django import forms

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
    class Meta:
        model = EmployerOnboardingProfile
        fields = ("preferred_location", "preferred_start_date", "preferred_time", "special_instructions")
        widgets = {
            "preferred_location": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Area, suburb, or city"}),
            "preferred_start_date": forms.DateInput(attrs={"class": "mk-input", "type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"class": "mk-input", "type": "time"}),
            "special_instructions": forms.Textarea(attrs={"class": "mk-input", "rows": 4, "placeholder": "Any specific instructions"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_location"].required = True
        self.fields["preferred_start_date"].required = True
        self.fields["preferred_time"].required = True


class HelperProfileForm(forms.ModelForm):
    class Meta:
        model = HelperOnboardingProfile
        fields = ("display_name", "location", "years_experience", "bio")
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Display name"}),
            "location": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Area, suburb, or city"}),
            "years_experience": forms.NumberInput(attrs={"class": "mk-input", "min": 0, "max": 60}),
            "bio": forms.Textarea(attrs={"class": "mk-input", "rows": 4, "placeholder": "Short profile summary"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["display_name"].required = True
        self.fields["location"].required = True
        self.fields["years_experience"].required = True
        self.fields["bio"].required = True

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

    class Meta:
        model = HelperOnboardingProfile
        fields = ("selected_categories", "preferred_work_area", "availability_summary")
        widgets = {
            "preferred_work_area": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Preferred work area"}),
            "availability_summary": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Example: Weekdays, 08:00-16:00"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_work_area"].required = True
        self.fields["availability_summary"].required = True
        if self.instance and self.instance.selected_categories:
            self.fields["selected_categories"].initial = self.instance.categories_list()

    def clean_selected_categories(self):
        categories = self.cleaned_data.get("selected_categories") or []
        if not categories:
            raise forms.ValidationError("Select at least one category.")
        return categories

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_categories = ",".join(self.cleaned_data["selected_categories"])
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
