import json

from django.urls import reverse

from v1.accounts.tests.base import BaseTestCase
from v1.forms.constants import FormFieldType
from v1.forms.constants import FormType


class FormTestCase(BaseTestCase):
    def test_forms(self):
        reverse("forms-list")
        response = self.client.get(reverse("forms-list"), **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_create_forms(self):
        url = reverse("forms-list")
        data = {
            "form_type": FormType.TRANSACTION,
            "owner": self.company.id.hashid,
            "fields": [
                {
                    "label": self.faker.name(),
                    "type": FormFieldType.TEXT,
                    "key": self.faker.name(),
                    "required": True,
                    "default_value": self.faker.name(),
                }
                for f in range(5)
            ],
            "field_config": [
                {
                    "label": self.faker.name(),
                    "key": self.faker.name(),
                    "required": True,
                    "visibility": True,
                }
                for f in range(5)
            ],
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 201)
