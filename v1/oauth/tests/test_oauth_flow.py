import base64
import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from mixer.backend.django import mixer
from oauth2_provider.generators import generate_client_secret
from oauth2_provider.scopes import get_scopes_backend
from rest_framework.test import APITestCase

from v1.oauth.models import ClientServer


User = get_user_model()


class OAthTestCase(APITestCase):

    faker = Faker()
    access_token = ""
    refresh_token = ""
    expires_on = timezone.now()

    def setUp(self):
        self.device_id = self.faker.ean13()
        self.createUser()
        self.createCompany()
        self.createClientServer()

    def createUser(self):
        self.email = self.faker.email()
        self.password = self.faker.password()
        self.user = mixer.blend(User, email=self.email, username=self.email)
        self.user.set_password(self.password)
        self.user.save()

    def createCompany(self):
        self.company = mixer.blend(
            "supply_chains.Company", name=self.faker.company()
        )

    def createClientServer(self):
        self.secret = generate_client_secret()
        self.client_server = mixer.blend(
            ClientServer,
            client_secret=self.secret,
            client_type=ClientServer.CLIENT_CONFIDENTIAL,
            authorization_grant_type=ClientServer.GRANT_CLIENT_CREDENTIALS,
            user=self.user,
            scope=" ".join(get_scopes_backend().get_all_scopes().keys()),
        )
        mixer.blend(
            "oauth.ClientServerCompany",
            client_server=self.client_server,
            company=self.company,
        )

    def test_oauth_flow(self):
        url = reverse("token")
        credential = f"{self.client_server.client_id}:{self.secret}"
        token = base64.b64encode(credential.encode("utf-8"))
        data = {
            "grant_type": "client_credentials",
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION="Basic " + token.decode("utf-8"),
            HTTP_X_ENTITY_ID=self.company.id,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data.get("access_token"))

    @property
    def headers(self):
        return {
            "HTTP_AUTHORIZATION": f"Bearer {self.access()}",
        }

    @classmethod
    def loadCurrencies(cls):
        from scripts import load_currencies

        load_currencies.run()
