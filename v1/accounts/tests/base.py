from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from mixer.backend.django import mixer
from rest_framework.test import APITestCase


User = get_user_model()


class BaseTestCase(APITestCase):

    faker = Faker()
    access_token = ""
    refresh_token = ""
    expires_on = timezone.now()

    def setUp(self):
        self.device_id = self.faker.ean13()
        self.createUser()
        self.createCompanyForUser()

    def createUser(self):
        self.email = self.faker.email()
        self.password = self.faker.password()
        self.user = mixer.blend(User, email=self.email, username=self.email)
        self.user.set_password(self.password)
        self.user.save()

    def createCompanyForUser(self, user=None):
        if not user:
            user = self.user
        self.company = mixer.blend(
            "supply_chains.Company", name=self.faker.company()
        )
        mixer.blend(
            "supply_chains.CompanyMember", user=user, company=self.company
        )

    def login(self):
        url = reverse("login")
        data = {
            "username": self.email,
            "password": self.password,
            "device_id": self.device_id,
        }
        response = self.client.post(url, data)
        if response.status_code == 200:
            self.access_token = response.data["access"]
            self.refresh_token = response.data["refresh"]
            expires_in = int(response.data["expires_in"])
            self.expires_on = timezone.now() + timezone.timedelta(
                seconds=expires_in
            )

    def refresh(self):
        url = reverse("token_refresh")
        data = {"refresh": self.refresh_token, "entity": self.company.id}
        response = self.client.post(url, data)
        if response.status_code == 200:
            self.access_token = response.data["access"]
            expires_in = int(response.data["expires_in"])
            self.expires_on = timezone.now() + timezone.timedelta(
                seconds=expires_in
            )
        else:
            self.login()

    def access(self):
        if not self.access_token:
            self.login()
        if self.expires_on < timezone.now():
            self.refresh()
        return self.access_token

    @property
    def headers(self):
        return {
            "HTTP_AUTHORIZATION": f"Bearer {self.access()}",
        }

    @classmethod
    def loadCurrencies(cls):
        from scripts import load_currencies

        load_currencies.run()
