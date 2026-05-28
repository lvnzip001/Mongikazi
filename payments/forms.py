from django import forms

from payments.models import Payment


class PaymentProofForm(forms.Form):
    method = forms.ChoiceField(choices=Payment.Method.choices, widget=forms.Select(attrs={"class": "mk-input"}))
    amount = forms.DecimalField(max_digits=9, decimal_places=2, min_value=0, widget=forms.NumberInput(attrs={"class": "mk-input", "step": "0.01"}))
    payer_reference = forms.CharField(max_length=80, required=False, widget=forms.TextInput(attrs={"class": "mk-input", "placeholder": "Bank reference (optional)"}))
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "mk-input", "rows": 3, "placeholder": "Any payment notes"}))
    document_url = forms.URLField(required=False, widget=forms.URLInput(attrs={"class": "mk-input", "placeholder": "Proof URL (optional)"}))


class OperationsPayoutForm(forms.Form):
    payout_reference = forms.CharField(
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"class": "mk-input", "placeholder": "Payout batch/reference (optional)"}),
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "mk-input", "rows": 2, "placeholder": "Payout note (optional)"}),
    )




