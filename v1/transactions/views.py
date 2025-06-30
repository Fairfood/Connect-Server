from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.response import Response

from base.request_handler.response import SuccessResponse
from base.request_handler.views import IDDEcodeScopeViewset
from v1.transactions.filters import (PaymentTransactionFilterSet,
                                     ProductTransactionFilterSet)
from v1.transactions.models.payment_models import PaymentTransaction
from v1.transactions.models.transaction_models import ProductTransaction
from v1.transactions.serializers import (PaymentTransactionsSerializer,
                                         ProductTransactionSerializer)

# from rest_framework.response import Response


class ProductTransactionViewSet(IDDEcodeScopeViewset):
    """ViewSet for managing payment transactions.

    This ViewSet provides CRUD operations for payment transactions and
    includes a custom action 'invoice' for uploading invoice files.
    """

    queryset = ProductTransaction.objects.filter(is_deleted=False)
    serializer_class = ProductTransactionSerializer
    http_method_names = ("get", "post", "patch", "delete")
    resource_types = ["transaction"]
    filterset_class = ProductTransactionFilterSet

    def get_queryset(self):
        """
        Override queryset to sync deleted transaction to trace via 
        reverse sync
        """
        reverse_sync = self.request.query_params.get('reverse_sync', False)
        queryset = ProductTransaction.objects.all()
        if not reverse_sync:
            queryset = queryset.filter(is_deleted=False)
        return queryset

    @action(detail=True, methods=["patch"])
    def invoice(self, request, **kwargs):
        """Custom action to upload invoice for a payment transaction.

        This action allows users to attach an invoice file to a payment
        transaction.
        """

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
            {"id": instance.id, "invoice": instance.invoice.url}
        )

    def perform_destroy(self, instance):
        """Marks the given instance as deleted by setting the 'is_deleted'
        attribute to True and saving the instance.

        Args:
            instance: The instance to be marked as deleted.

        Returns:
            None
        """
        if not instance.children.exists():
            instance.is_deleted = True
            instance.save()
        else:
            raise ValidationError(
                "Cannot delete transaction with child transactions."
            )

    def destroy(self, request, *args, **kwargs):
        """Destroy a transaction instance.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

class PaymentTransactionViewSet(IDDEcodeScopeViewset):
    """ViewSet for managing payment transactions.

    This ViewSet provides CRUD operations for payment transactions and
    includes a custom action 'invoice' for uploading invoice files.
    """

    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionsSerializer
    http_method_names = ("get", "post", "patch")
    resource_types = ["payment"]
    filterset_class = PaymentTransactionFilterSet

    @action(detail=True, methods=["patch"])
    def invoice(self, request, **kwargs):
        """Custom action to upload invoice for a payment transaction.

        This action allows users to attach an invoice file to a payment
        transaction.
        """

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
            {"id": instance.id, "invoice": instance.invoice.url}
        )
