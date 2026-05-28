from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking
from employers.models import EmployerProfile
from helpers.models import HelperProfile, ServiceCategory


class EmployerBookingRequestForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "request_type",
            "worker",
            "service_category",
            "employer_location",
            "scheduled_date",
            "start_time",
            "duration_hours",
            "special_instructions",
        ]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date", "class": "mk-input"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "mk-input"}),
            "duration_hours": forms.NumberInput(attrs={"min": 1, "class": "mk-input"}),
            "special_instructions": forms.Textarea(attrs={"rows": 4, "class": "mk-input", "placeholder": "Gate code, focus areas, parking notes..."}),
            "request_type": forms.Select(attrs={"class": "mk-input"}),
            "worker": forms.Select(attrs={"class": "mk-input"}),
            "service_category": forms.Select(attrs={"class": "mk-input"}),
            "employer_location": forms.Select(attrs={"class": "mk-input"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.fields["worker"].queryset = HelperProfile.objects.filter(is_active=True).select_related("user")
        self.fields["service_category"].queryset = ServiceCategory.objects.filter(is_active=True)

        employer_profile = EmployerProfile.objects.filter(user=user).first() if user else None
        if employer_profile:
            self.fields["employer_location"].queryset = employer_profile.locations.filter(is_active=True)
        else:
            self.fields["employer_location"].queryset = self.fields["employer_location"].queryset.none()

        self.fields["worker"].empty_label = "Select worker"
        self.fields["service_category"].empty_label = "Select service"
        self.fields["employer_location"].empty_label = "Select location"
        self.fields["request_type"].choices = [
            (Booking.RequestType.DIRECT_REQUEST, "Direct request (choose helper)"),
            (Booking.RequestType.OPEN_MARKETPLACE, "Open marketplace (helpers apply)"),
        ]

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data["scheduled_date"]
        if scheduled_date < timezone.localdate():
            raise ValidationError("Scheduled date cannot be in the past.")
        return scheduled_date

    def clean_duration_hours(self):
        duration_hours = self.cleaned_data["duration_hours"]
        if duration_hours <= 0:
            raise ValidationError("Duration must be greater than zero.")
        return duration_hours

    def clean_worker(self):
        worker = self.cleaned_data["worker"]
        request_type = self.cleaned_data.get("request_type")
        if request_type == Booking.RequestType.OPEN_MARKETPLACE and not worker:
            return worker
        if not worker:
            raise ValidationError("Select a worker for direct requests.")
        if not worker.is_active:
            raise ValidationError("Selected worker is not active.")
        return worker

    def clean_service_category(self):
        category = self.cleaned_data["service_category"]
        if not category.is_active:
            raise ValidationError("Selected service category is not active.")
        return category

    def clean_employer_location(self):
        location = self.cleaned_data["employer_location"]
        employer_profile = EmployerProfile.objects.filter(user=self.user).first() if self.user else None
        if not employer_profile or location.employer_id != employer_profile.id:
            raise ValidationError("Selected location is not valid for this employer.")
        return location

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get("request_type")
        worker = cleaned_data.get("worker")
        category = cleaned_data.get("service_category")
        if request_type == Booking.RequestType.DIRECT_REQUEST and not worker:
            self.add_error("worker", "Worker is required for direct requests.")
        if worker and category and worker.skills.exists() and not worker.skills.filter(category=category).exists():
            self.add_error("service_category", "Worker does not currently list this service category.")
        return cleaned_data


class BookingApplicationForm(forms.Form):
    message = forms.CharField(
        required=False,
        max_length=600,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "mk-input",
                "placeholder": "Short note introducing your availability and fit...",
            }
        ),
    )
    proposed_fee = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=9,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "class": "mk-input", "placeholder": "Optional proposed fee"}),
    )


class WorkerDeclineBookingForm(forms.Form):
    reason = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={"rows": 3, "class": "mk-input"}))


class EmployerCancelBookingForm(forms.Form):
    reason = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={"rows": 3, "class": "mk-input"}))


class WorkerCancelBookingForm(forms.Form):
    reason = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={"rows": 3, "class": "mk-input"}))
