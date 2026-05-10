from django import forms

from .models import HelperAvailability, HelperProfile, HelperSkill


class HelperProfileForm(forms.ModelForm):
    class Meta:
        model = HelperProfile
        fields = (
            "display_name",
            "profile_photo",
            "location",
            "preferred_work_area",
            "bio",
            "years_experience",
            "availability_summary",
            "is_active",
        )
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Display name"}),
            "location": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Location"}),
            "preferred_work_area": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Preferred work area"}),
            "bio": forms.Textarea(attrs={"class": "mk-input", "rows": 4, "placeholder": "Profile bio"}),
            "years_experience": forms.NumberInput(attrs={"class": "mk-input", "min": 0}),
            "availability_summary": forms.TextInput(attrs={"class": "mk-input", "placeholder": "Availability summary"}),
        }

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
