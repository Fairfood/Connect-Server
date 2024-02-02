import json

from django.urls import reverse
from mixer.backend.django import mixer

from v1.accounts.tests.base import BaseTestCase
from v1.catalogs.constants import PremiumCategory
from v1.forms.constants import FormType
from v1.supply_chains.constants import CompanyMemberType


class SupplyChainTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        print("\n")
        cls.loadCurrencies()

    def test_entity_cards(self):
        url = reverse("entity-cards-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_companies(self):
        url = reverse("companies-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_farmers(self):
        url = reverse("farmers-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_create_company_members(self):
        url = reverse("company-members-list")
        data = {
            "company": self.company.id.hashid,
            "type": CompanyMemberType.SUPER_ADMIN,
            "user": {
                "email": self.faker.email(),
                "first_name": self.faker.first_name(),
                "last_name": self.faker.last_name(),
                "phone": self.faker.phone_number(),
                "dob": self.faker.date_of_birth().isoformat(),
                "address": self.faker.address(),
            },
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def test_create_company_products(self):
        url = reverse("company-products-list")
        premium = mixer.blend(
            "catalogs.Premium",
            owner=self.company,
            category=PremiumCategory.TRANSACTION,
        )
        data = {
            "product": {
                "name": self.faker.name(),
                "description": self.faker.text(),
            },
            "company": self.company.id.hashid,
            "premiums": [premium.id.hashid],
            "is_active": True,
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def test_create_company(self):
        url = reverse("companies-list")
        data = {
            "name": self.faker.company(),
            "house_name": self.faker.name(),
            "street": self.faker.street_name(),
            "city": self.faker.city(),
            "sub_province": self.faker.city(),
            "province": self.faker.city(),
            "latitude": float(self.faker.latitude()),
            "longitude": float(self.faker.longitude()),
            "zipcode": self.faker.postcode(),
            "country": self.faker.country(),
            "email": self.faker.email(),
            "phone": self.faker.phone_number(),
            "description": self.faker.text(),
            "buyer": self.company.id.hashid,
            "currency": "EUR",
            "sell_enabled": True,
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def test_create_farmer(self):
        url = reverse("farmers-list")
        data = {
            "created_on": self.faker.date_time().timestamp(),
            "description": self.faker.text(),
            "house_name": self.faker.name(),
            "street": self.faker.street_name(),
            "city": self.faker.city(),
            "sub_province": self.faker.city(),
            "province": self.faker.city(),
            "latitude": float(self.faker.latitude()),
            "longitude": float(self.faker.longitude()),
            "zipcode": self.faker.postcode(),
            "country": self.faker.country(),
            "email": self.faker.email(),
            "phone": self.faker.phone_number(),
            "identification_no": self.faker.ean13(),
            "reference_number": self.faker.ean13(),
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "date_of_birth": self.faker.date_of_birth().isoformat(),
            "gender": self.faker.random_element(elements=("M", "F")),
            "consent_status": "GRANTED",
            "buyer": self.company.id.hashid,
            "creator": self.user.id.hashid,
        }

        self._create_form()
        data["submission"] = {
            "form": self.form.id.hashid,
            "values": [
                {
                    "value": self.faker.name(),
                    "field": self.form_field.id.hashid,
                }
            ],
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def _create_form(self):
        self.form = mixer.blend(
            "forms.Form", form_type=FormType.FARMER, owner=self.company
        )
        self.form_field = mixer.blend("forms.FormField", form=self.form)

    def test_create_entity_card(self):
        url = reverse("entity-cards-list")
        farmer = mixer.blend("supply_chains.Farmer", buyer=self.company)
        data = {
            "entity": farmer.id.hashid,
            "card": {
                "card_id": self.faker.ean13(),
                "disply_id": self.faker.ean13(),
            },
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 201)

    def test_patch_farmer(self):
        farmer = mixer.blend("supply_chains.Farmer", buyer=self.company)
        url = reverse("farmers-detail", args=(farmer.id.hashid,))
        data = {
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
        }
        response = self.client.patch(url, data, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_patch_company(self):
        url = reverse("companies-detail", args=(self.company.id.hashid,))
        data = {
            "name": self.faker.company(),
            "house_name": self.faker.name(),
        }
        response = self.client.patch(url, data, **self.headers)
        self.assertEqual(response.status_code, 200)
