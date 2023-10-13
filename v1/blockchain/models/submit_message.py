""" Custom Models for Creating Blockchain Key """
from sentry_sdk import capture_exception
from django.db import models

from .. import library
from .. import constants

from .callback_auth import CallBackToken
from .request import BlockchainRequest

from ..constants import HEDERA_CONSENSUS_MESSAGE_SIZE

# Create your models here.


class SubmitMessageRequest(BlockchainRequest):
    """ Request Model for creating token for a product in the blockchain"""
    action = constants.ACTION_CREATE_CONSENSUS

    def prepare_body(self):
        """ Over-ridden prepare_body to format body for the corresponding reques type """
        related_object = getattr(self, self.object_related_name.lower())
        body = super(SubmitMessageRequest, self).prepare_body()

        message = related_object.message
        if len(message) > HEDERA_CONSENSUS_MESSAGE_SIZE:
            try:
                message = related_object.short_message
            except:
                message = message[:HEDERA_CONSENSUS_MESSAGE_SIZE]

        params = {}
        params['topic_id'] = related_object.topic_id
        params['message'] = message

        body['params'] = params
        self.body = body
        self.save()
        return body

    def handle_response(self, response):
        """ Function implemented in the subclass to handle response format """
        related_object = getattr(self, self.object_related_name.lower())
        return related_object.update_message_hash(response['data'])


class AbstractConsensusMessage(models.Model):
    """
    Abstract base class for Blockchain Key to be imported to corresponding
    model inside the project
    """

    submit_message_request = models.OneToOneField(
        BlockchainRequest, related_name='%(app_label)s_%(class)s_msg_req', null=True, blank=True,
        default=None, on_delete=models.SET_NULL)
    message_id = models.CharField(default='', max_length=500)
    message_hash = models.CharField(default='', max_length=500)

    class Meta:
        abstract = True

    def initialize_message(self, user=None):
        """
        CreateKeyRequest is created and saves in submit_message_request,
        object_related_name is set accordingly
        """
        if not self.submit_message_request:
            token = CallBackToken.objects.create()
            create_key_request = SubmitMessageRequest.objects.create(
                callback_token=token,
                object_related_name=f"{self._meta.app_label}_{self.__class__.__name__}_msg_req")
            self.submit_message_request = create_key_request
            self.save()
        else:
            self.submit_message_request.callback_token.refresh()
        return self.submit_message_request

    def message_pre_check(self):
        if not self.submit_message_request:
            return True, "Pre-check success"
        if self.submit_message_request.is_delayed():
            self.submit_message_request.discard()
            return True, "Pre-check success"
        if self.submit_message_request.status != constants.BC_REQUEST_STATUS_PENDING:
            return True, "Pre-check success"
        return False, "Pending request already exists"

    @property
    def topic_id(self):
        """ To be implemented in the subclass to return name """
        raise NotImplementedError()

    @property
    def message(self):
        """ To be implemented in the subclass to return name """
        raise NotImplementedError()

    def submit_info_message(self):
        success, message = self.message_pre_check()
        if not success:
            return False
        try:
            self.initialize_message()
            self.submit_message_request.send()
            return True
        except Exception as e:
            capture_exception(e)
            return False

    def update_message_hash(self, bc_data):
        """ to update hash on callback from blockchain entity """
        self.message_id = bc_data['transactionId']
        self.message_hash = bc_data['transactionHash']
        self.save()
        return True
