from django.core.management.base import BaseCommand
from django.utils.text import slugify

from locations.models import Locality
from locations.seed_data.sa_localities import SA_LOCALITIES


class Command(BaseCommand):
    help = "Seed or update South African localities for autocomplete and matching."

    def add_arguments(self, parser):
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="Mark localities not in the seed file as inactive (does not delete).",
        )

    def handle(self, *args, **options):
        seen_slugs = set()
        created = 0
        updated = 0

        for row in SA_LOCALITIES:
            name, province, locality_type, municipality, sort_order = row
            slug = slugify(f"{name}-{province}")[:160]
            seen_slugs.add(slug)
            defaults = {
                "name": name,
                "province": province,
                "locality_type": locality_type,
                "municipality": municipality or "",
                "sort_order": sort_order,
                "is_active": True,
            }
            locality, was_created = Locality.objects.update_or_create(slug=slug, defaults=defaults)
            locality.save()
            if was_created:
                created += 1
            else:
                updated += 1

        deactivated = 0
        if options["deactivate_missing"]:
            deactivated = (
                Locality.objects.exclude(slug__in=seen_slugs)
                .filter(is_active=True)
                .update(is_active=False)
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Localities: {created} created, {updated} updated, {deactivated} deactivated."
            )
        )
