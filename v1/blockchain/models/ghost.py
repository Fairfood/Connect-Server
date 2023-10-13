
from sentry_sdk import capture_message

from django.conf import settings

from .. import constants


class ReqList:
    """
    for representation only
    """
    requests = []

    def add(self, item):
        self.requests.add(item)


class TreasuryWallet:
    account_id = settings.TREASURY_ACCOUNT_ID
    public = ""
    private = settings.TREASURY_ENCRYPED_PRIVATE

    deferred_requests = ReqList()

    def topup_hbar(self):
        capture_message("Balance low in treasury account")
