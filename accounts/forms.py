from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


def normalize_phone_number(value):
    """Light normalisation for MVP without external dependencies."""
    cleaned = (value or "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    return cleaned


class MongiKaziLoginForm(forms.Form):
    identifier = forms.CharField(
        label="Email, phone number, or username",
        widget=forms.TextInput(
            attrs={
                "class": "mk-input",
                "placeholder": "Email, phone number, or username",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "mk-input",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        identifier = (cleaned_data.get("identifier") or "").strip()
        password = cleaned_data.get("password")

        if identifier and password:
            username = identifier
            phone_identifier = normalize_phone_number(identifier)
            user_match = (
                User.objects.filter(email__iexact=identifier).first()
                or User.objects.filter(phone_number=phone_identifier).first()
                or User.objects.filter(username__iexact=identifier).first()
            )
            if user_match:
                username = user_match.get_username()

            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a valid email, phone number, or username with password.")
            if not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label="First name",
        widget=forms.TextInput(attrs={"class": "mk-input", "placeholder": "First name", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        label="Surname",
        widget=forms.TextInput(attrs={"class": "mk-input", "placeholder": "Surname", "autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"class": "mk-input", "placeholder": "Email address", "autocomplete": "email"}),
    )
    phone_number = forms.CharField(
        label="Phone number",
        widget=forms.TextInput(attrs={"class": "mk-input", "placeholder": "Phone number", "autocomplete": "tel"}),
    )
    accepted_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-mk-border text-mk-primary focus:ring-mk-primary"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "phone_number", "password1", "password2", "accepted_terms")

    def __init__(self, *args, role=None, **kwargs):
        self.role = (role or User.Role.EMPLOYER).upper()
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "mk-input", "placeholder": "Password", "autocomplete": "new-password"})
        self.fields["password2"].widget.attrs.update({"class": "mk-input", "placeholder": "Confirm password", "autocomplete": "new-password"})

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = normalize_phone_number(self.cleaned_data["phone_number"])
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        if self.role not in {User.Role.EMPLOYER, User.Role.HELPER}:
            raise forms.ValidationError("Please choose a valid MongiKazi account type.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower().strip()
        user.username = user.email
        user.phone_number = self.cleaned_data["phone_number"]
        user.role = self.role
        user.accepted_terms = self.cleaned_data["accepted_terms"]
        if commit:
            user.save()
            self.save_m2m()
        return user
