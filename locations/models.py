from django.db import models
from django.utils.text import slugify


class Locality(models.Model):
    """South African suburb/city/town — maintained in admin and seed data."""

    class LocalityType(models.TextChoices):
        SUBURB = "suburb", "Suburb"
        CITY = "city", "City"
        TOWN = "town", "Town"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=160, unique=True)
    province = models.CharField(max_length=80)
    municipality = models.CharField(max_length=120, blank=True)
    locality_type = models.CharField(
        max_length=20,
        choices=LocalityType.choices,
        default=LocalityType.SUBURB,
    )
    search_text = models.CharField(max_length=300, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name_plural = "localities"
        indexes = [
            models.Index(fields=["is_active", "name"]),
            models.Index(fields=["is_active", "province"]),
        ]

    def __str__(self):
        return self.display_label

    @property
    def display_label(self):
        return f"{self.name}, {self.province}"

    def build_search_text(self):
        parts = [self.name, self.province, self.municipality, self.get_locality_type_display()]
        return " ".join(part for part in parts if part).lower()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.province}")[:160]
        self.search_text = self.build_search_text()
        super().save(*args, **kwargs)
