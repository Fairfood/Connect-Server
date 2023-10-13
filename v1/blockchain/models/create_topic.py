""" Custom Models for Creating Heddera Topic """

from sentry_sdk import capture_message
from sentry_sdk import capture_exception
from django.db import models
from .. import library
from .. import constants

from .callback_auth import CallBackToken
from .ghost import TreasuryWallet
from .request import BlockchainRequest

# Create your models here.


class CreateTopicRequest(BlockchainRequest):
    """ Request Model for creating topic for a product in the blockchain"""
    action = constants.ACTION_CREATE_TOPIC

    def prepare_body(self):
        """ Over-ridden prepare_body to format body for the corresponding reques type """
        related_object = getattr(self, self.object_related_name.lower())
        body = super(CreateTopicRequest, self).prepare_body()

        params = {}
        params['memo'] = related_object.topic_name

        body['params'] = params
        self.body = body
        self.save()
        return body

    def handle_response(self, response):
        """ Function implemented in the subclass to handle response format """
        related_object = getattr(self, self.object_related_name.lower())
        return related_object.update_topic_id(response['data'])


class AbstractTopic(models.Model):
    """
    Abstract base class for Blockchain Key to be imported to corresponding
    model inside the project
    """

    block_chain_request = models.OneToOneField(
        BlockchainRequest, related_name='%(app_label)s_%(class)s', null=True, blank=True,
        default=None, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    def initialize(self, user=None):
        """
        CreateKeyRequest is created and saves in block_chain_request,
        object_related_name is set accordingly
        """
        if not self.block_chain_request:
            token = CallBackToken.objects.create(creator=user)
            create_key_request = CreateTopicRequest.objects.create(
                callback_token=token, creator=user,
                object_related_name=f"{self._meta.app_label}_{self.__class__.__name__}")
            self.block_chain_request = create_key_request
            self.save()
        else:
            self.block_chain_request.callback_token.refresh()
        return self.block_chain_request

    def pre_check(self):
        if not self.block_chain_request:
            return True, "Pre-check success"
        if self.block_chain_request.is_delayed():
            self.block_chain_request.discard()
            return True, "Pre-check success"
        if self.block_chain_request.status != constants.BC_REQUEST_STATUS_PENDING:
            return True, "Pre-check success"
        return False, "Pending request already exists"

    def create_topic(self):
        success, message = self.pre_check()
        if not success:
            return False
        try:
            self.initialize()
            self.block_chain_request.send()
            return True
        except Exception as e:
            print(e)
            capture_exception(e)
            return False

    @property
    def topic_name(self):
        """ To be implemented in the subclass to return name """
        raise NotImplementedError()

    def update_topic_id(self, bc_hash):
        """ To be implemented in the subclass to update hash when callback is received """
        raise NotImplementedError()

    @property
    def initiator_wallet(self):
        """ The initiator is the project itself"""
        return TreasuryWallet()
