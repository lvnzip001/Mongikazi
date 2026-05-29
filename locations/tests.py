from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from locations.models import Locality
from locations.selectors import search_localities


class LocalityTests(TestCase):
    def setUp(self):
        Locality.objects.create(
            name="Benoni",
            province="Gauteng",
            municipality="Ekurhuleni",
            locality_type=Locality.LocalityType.SUBURB,
            sort_order=10,
        )

    def test_search_localities_finds_suburb(self):
        results = list(search_localities("ben"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Benoni")

    def test_autocomplete_requires_login(self):
        response = self.client.get(reverse("locations:autocomplete"), {"q": "ben"})
        self.assertEqual(response.status_code, 302)

    def test_autocomplete_returns_json(self):
        user = User.objects.create_user(
            username="helper@mk.com",
            email="helper@mk.com",
            password="StrongPass123!",
            role=User.Role.HELPER,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("locations:autocomplete"), {"q": "ben"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["label"], "Benoni, Gauteng")
