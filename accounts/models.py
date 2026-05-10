from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for MongiKazi role-based portal access."""

    class Role(models.TextChoices):
        EMPLOYER = "EMPLOYER", _("Employer")
        HELPER = "HELPER", _("Helper")
        OPERATIONS = "OPERATIONS", _("Operations")
        ADMIN = "ADMIN", _("Admin")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_onboarding_complete = models.BooleanField(default=False)
    accepted_terms = models.BooleanField(default=False)
    accepted_terms_at = models.DateTimeField(null=True, blank=True)

    # Explicit related names prevent reverse-accessor clashes if the project has not
    # yet switched settings.AUTH_USER_MODEL from auth.User to accounts.User.
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_("The groups this user belongs to. A user will get all permissions granted to each of their groups."),
        related_name="mongikazi_user_set",
        related_query_name="mongikazi_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="mongikazi_user_set",
        related_query_name="mongikazi_user",
    )

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["is_onboarding_complete"]),
        ]

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER

    @property
    def is_helper(self):
        return self.role == self.Role.HELPER

    @property
    def is_operations_user(self):
        return self.role in {self.Role.OPERATIONS, self.Role.ADMIN} or self.is_staff or self.is_superuser
