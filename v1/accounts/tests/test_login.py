from django.urls import reverse

from v1.accounts.tests.base import BaseTestCase


class AuthTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_login(self):
        self.login()
        self.assertTrue(self.access_token)
        self.assertTrue(self.refresh_token)

    def test_refresh(self):
        self.login()
        self.refresh()
        self.assertTrue(self.access_token)
        self.assertTrue(self.refresh_token)

    def test_verify(self):
        url = reverse("token_verify")
        data = {
            "token": self.access(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_change_password(self):
        self.login()
        url = reverse("password_change")
        new_passsword = self.faker.password()
        data = {
            "old_password": self.password,
            "new_password1": new_passsword,
            "new_password2": new_passsword,
        }
        response = self.client.post(url, data, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.password = new_passsword

    def test_reset_password(self):
        url = reverse("password_reset")
        data = {"email": self.email}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_sync_status(self):

        url = reverse("trace-sync-status")
        data = {"task_id": self.faker.ean13()}
        response = self.client.get(url, data=data, **self.headers)
        self.assertEqual(response.status_code, 405)
