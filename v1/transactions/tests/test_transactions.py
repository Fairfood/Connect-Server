from django.urls import reverse

from v1.accounts.tests.base import BaseTestCase


class TransactionTestCase(BaseTestCase):
    def test_product_transactions(self):
        url = reverse("product-transactions-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)

    def test_payment_transactions(self):
        url = reverse("payment-transactions-list")
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)
