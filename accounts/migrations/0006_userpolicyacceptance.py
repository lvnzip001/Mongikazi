from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_profile_photos"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPolicyAcceptance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "source",
                    models.CharField(
                        choices=[("REGISTRATION", "Registration")],
                        default="REGISTRATION",
                        max_length=24,
                    ),
                ),
                ("terms_version", models.CharField(max_length=32)),
                ("privacy_version", models.CharField(max_length=32)),
                ("safety_version", models.CharField(max_length=32)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=512)),
                ("accepted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="policy_acceptances",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="userpolicyacceptance",
            index=models.Index(fields=["user", "accepted_at"], name="accounts_use_user_id_8e5290_idx"),
        ),
        migrations.AddIndex(
            model_name="userpolicyacceptance",
            index=models.Index(fields=["accepted_at"], name="accounts_use_accepte_8ef76f_idx"),
        ),
    ]
