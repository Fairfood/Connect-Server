import json

from django.urls import reverse

from v1.accounts.tests.base import BaseTestCase
from v1.catalogs.constants import PremiumActivity
from v1.catalogs.constants import PremiumCalculationType
from v1.catalogs.constants import PremiumCategory
from v1.catalogs.constants import PremiumType


class CatalogTestCase(BaseTestCase):
    def test_currency(self):
        url = reverse("currencies-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_product(self):
        url = reverse("products-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_premium(self):
        url = reverse("premiums-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_connect_card(self):
        url = reverse("connect-cards-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_create_premium(self):
        url = reverse("premiums-list")
        data = {
            "category": PremiumCategory.PAYOUT,
            "name": self.faker.name(),
            "type": PremiumType.PER_TRANSACTION,
            "amount": self.faker.pyfloat(),
            "included": True,
            "dependant_on_card": True,
            "applicable_activity": PremiumActivity.BUY,
            "calculation_type": PremiumCalculationType.OPTIONS,
            "is_active": True,
            "owner": self.company.id.hashid,
            "options": [
                {
                    "name": self.faker.name(),
                    "amount": self.faker.pyfloat(),
                    "is_active": True,
                },
                {
                    "name": self.faker.name(),
                    "amount": self.faker.pyfloat(),
                    "is_active": True,
                },
            ],
        }

        response = self.client.post(
            url,
            json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def test_create_connect_card(self):
        url = reverse("connect-cards-list")
        data = {
            "card_id": self.faker.ean13(),
            "disply_id": self.faker.name(),
        }

        response = self.client.post(url, data, **self.headers)
        self.assertEqual(response.status_code, 201)
