from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from base.request_handler.response import SuccessResponse
from base.request_handler.views import IdDecodeModelViewSet
from v1.transactions.models.payment_models import PaymentTransaction
from v1.transactions.models.transaction_models import ProductTransaction
from v1.transactions.serializers import PaymentTransactionsSerializer
from v1.transactions.serializers import ProductTransactionSerializer


class ProductTransactionViewSet(IdDecodeModelViewSet):
    queryset = ProductTransaction.objects.all()
    serializer_class = ProductTransactionSerializer
    http_method_names = ("get", "post")
    # filterset_class = ProductTransactionFilterSet

    @action(detail=True, methods=["patch"])
    def invoice(self, request, **kwargs):
        """Adding separate API for uploading invoice."""

        # getting file from request.
        invoice = request.data.get("invoice")
        if not invoice and not invoice.file:
            raise ValidationError("No invoice attached.")

        # Using serializer to update with instance
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data={"invoice": invoice},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return SuccessResponse(
            {"id": instance.idencode, "invoice": instance.invoice.url}
        )


class PaymentTransactionViewSet(IdDecodeModelViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionsSerializer
    http_method_names = ("get", "post")

    @action(detail=True, methods=["patch"])
    def invoice(self, request, **kwargs):
        """Adding separate API for uploading invoice."""

        # getting file from request.
        invoice = request.data.get("invoice")
        if not invoice and not invoice.file:
            raise ValidationError("No invoice attached.")

        # Using serializer to update with instance
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data={"invoice": invoice},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return SuccessResponse(
            {"id": instance.idencode, "invoice": instance.invoice.url}
        )
