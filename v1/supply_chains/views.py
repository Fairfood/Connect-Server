import csv
import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sentry_sdk import capture_message

from base.authentication import utilities as utils
from base.permissions import ValidTOTP
from base.exceptions.custom_exceptions import BadRequest, Conflict
from base.request_handler.views import IDDEcodeScopeViewset
from utilities.functions import decode
from v1.supply_chains.models.base_models import EntityBuyer, EntityCard, Entity
from v1.supply_chains.models.company_models import (Company, CompanyMember,
                                                    CompanyProduct)
from v1.supply_chains.models.farmer_models import Farmer
from v1.supply_chains.serializers import (AppFarmerSerializer,
                                          CompanyCreateSerializer,
                                          CompanyMemerMiniSerializer,
                                          CompanyMemerSerializer,
                                          CompanyProductSerializer,
                                          CompanySerializer,
                                          EntityBuyerSerializer,
                                          EntityCardSerializer,
                                          FarmerSerializer,
                                          OpenTransactionSerializer)
from v1.supply_chains.constants import FarmerConsentStatus
from v1.transactions.models.transaction_models import ProductTransaction

from .filters import (EntityCardFilterSet, FarmerFilterSet,
                      OpenFilterTransactions)


class EntityCardViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing EntityCard instances."""

    queryset = EntityCard.objects.all()
    serializer_class = EntityCardSerializer
    http_method_names = ("get", "post")
    resource_types = ["company", "farmer"]
    filterset_class = EntityCardFilterSet


class CompanyViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing Company instances.

    This viewset extends the IdDecodeModelViewSet and provides
    customization for viewing and editing Company instances in the API.
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    http_method_names = (
        "get",
        "post",
        "patch",
    )
    resource_types = ["company"]

    def get_serializer_class(self):
        """Get the serializer class based on the action.

        Returns the CompanyCreateSerializer for create, update,
        and partial_update actions, and the default CompanySerializer for
        other actions.

        Returns:
            Serializer: The appropriate serializer class based on the action.
        """
        if self.action in ["create", "update", "partial_update", "buyer_create"]:
            return CompanyCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        if "name" not in request.data or not request.data["name"].strip():
            raise serializers.ValidationError({"name": _("This field is required.")})
        company_obj = Company.objects.filter(name=request.data["name"].strip()).first()
        if company_obj:
            serializer = CompanySerializer(instance=company_obj)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    @action(methods=("post",), detail=False, url_path="buyer")
    def buyer_create(self, request):
        """
        Create a new company as buyer
        """
        source_company_id = request.data.pop("source_company_id", None)
        source_company = Company.objects.filter(id=source_company_id).first()
        if not source_company:
            source_company = utils.get_current_entity()
        if "name" not in request.data or not request.data["name"].strip():
            raise serializers.ValidationError({"name": _("This field is required.")})
        company = Company.objects.filter(name=request.data["name"].strip()).first()
        if not company:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            company = serializer.save()
        else:
            serializer = CompanySerializer(instance=company)
        if company and source_company:
            if not EntityBuyer.objects.filter(entity=source_company, buyer=company).exists():
                data = {
                    "entity" : source_company,
                    "buyer" : company
                }
                if not EntityBuyer.objects.filter(entity=source_company, is_default=True).exists():
                    data["is_default"] =  True
                eb_obj = EntityBuyer.objects.create(**data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    @action(methods=("post",), detail=False, url_path="map-buyer")
    def map_buyer(self, request):
        """
        Create a new company as buyer
        """
        extra_args = {}
        extra_args['context'] = self.get_serializer_context()
        serializer = EntityBuyerSerializer(data=request.data, **extra_args)
        serializer.is_valid(raise_exception=True)
        entity_buyer_obj = serializer.save()
        if not EntityBuyer.objects.filter(entity=serializer.validated_data["entity"], is_default=True).exists():
            entity_buyer_obj.is_default = True
            entity_buyer_obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FarmerViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing Farmer instances."""

    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    http_method_names = (
        "get",
        "post",
        "patch",
    )
    resource_types = ["farmer"]
    filterset_class = FarmerFilterSet

    @action(methods=("post",), detail=False, url_path="bulk-create")
    def bulk_create(self, request):
        "bulk create"
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(["Created"], status=status.HTTP_201_CREATED)


class CompanyMemberViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing CompanyMember instances."""

    queryset = CompanyMember.objects.all()
    serializer_class = CompanyMemerMiniSerializer
    resource_types = ["company"]
    http_method_names = ("post",)


class CompanyProductViewSet(IDDEcodeScopeViewset):
    """A viewset for viewing and editing CompanyProduct instances."""

    queryset = CompanyProduct.objects.all()
    serializer_class = CompanyProductSerializer
    resource_types = ["company"]
    http_method_names = ("post",)


class FarmerDetailsAPI(generics.ListAPIView):
    """API to get app Farmer details."""

    serializer_class = AppFarmerSerializer
    permission_classes = (ValidTOTP,)

    def validate_dob(self, entity: Entity):
        """To validate dob for companies with 'make_farmers_private' enabled"""
        entities = Company.objects.filter(
            id__in=EntityBuyer.objects.filter(
                entity=entity
            ).values_list("buyer__id", flat=True),
            make_farmers_private=True
        ).distinct("id")

        # private farmers need extra check
        if any(entities):
            dob = self.request.data.get("dob", None)
            if not dob:
                raise BadRequest(
                    "Date of birth is required", 
                    send_to_sentry=False
                )

            if not entity.farmer.date_of_birth:
                raise Conflict("Date of birth not set", send_to_sentry=False)
            
            if entity.farmer.date_of_birth.strftime("%Y-%m-%d") != dob:
                raise Conflict("Incorrect DOB", send_to_sentry=False)

    def get_queryset(self):
        # """To perform function get_queryset."""
        try:
            fair_id = (
                str(self.kwargs["pk"]).upper().lstrip("FF").replace(" ", "")
            )
            entity = EntityCard.objects.filter(
                card__display_id__iexact=fair_id
            ).order_by('-created_on').first().entity
        except Exception:
            raise BadRequest("Invalid card number", send_to_sentry=False)
        
        if not Farmer.objects.filter(id=entity.id).exists():
            raise BadRequest(
                "No farmer associated with this card number.", 
                send_to_sentry=False
            )
        
        self.validate_dob(entity)
        
        return  Farmer.objects.filter(id=entity.id)

class CompanyMemberView(generics.ListAPIView):
    """A viewset for viewing and editing CompanyMember instances."""

    queryset = CompanyMember.objects.all()
    serializer_class = CompanyMemerSerializer
    http_method_names = ("get")

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(company=self.kwargs["pk"])
        return qs

class OpenTransactionAPI(generics.ListAPIView):
    """View for list transaction details of particular farmer.

    The farmer id is passing through params.
    """

    serializer_class = OpenTransactionSerializer
    permission_classes = (ValidTOTP,)
    filterset_class = OpenFilterTransactions

    def get_queryset(self):
        """To perform function get_queryset."""
        card_id = self.request.query_params.get("card_id", None)
        fair_id = card_id.upper().lstrip("FF").replace(" ", "")
        entity_card = EntityCard.objects.filter(card__display_id__iexact=fair_id).order_by('-created_on').first()
        if not entity_card:
            raise BadRequest("Invalid card number")
        if not entity_card.entity:
            raise BadRequest("Invalid card number")
        entity = entity_card.entity
        query = Q(source__id=entity.id) | Q(destination__id=entity.id)
        return ProductTransaction.objects.filter(is_deleted=False).filter(query).order_by("-date")
        
    
class OpenTransactionDetails(generics.ListAPIView):
    """View for transaction details."""

    serializer_class = OpenTransactionSerializer
    permission_classes = (ValidTOTP,)


    def get(self, request, *args, **kwargs):
        """function for get the details of transaction.


        and here transaction id in encrypted format. so decrypt id
        before filter Transaction.
        """
        trans_id = kwargs["pk"]
        try:
            transaction = ProductTransaction.objects.get(
                id=decode(trans_id))
        except Exception:
            raise BadRequest("Invalid Transaction id.")

        serializer = OpenTransactionSerializer(
            transaction, data=request.data, partial=True, context=self.kwargs
        )
        if not serializer.is_valid():
            raise BadRequest(serializer.errors)
        return Response(serializer.data)


class DownloadIncomingTransactionsView(APIView):
    """View to download incoming transactions of a company from djadmin"""
    
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        decoded_id = decode(kwargs.get('id', None))
        obj = get_object_or_404(Company, pk=decoded_id)

        # Prepare the data for the CSV
        input_variable = [
            ['ID', 'Source', 'Destination', 'Invoice Number', 'Date', 
             'Quality Correction', 'Product', 'Quantity', 'Currency', 
             'Reference', 'Base Price', 'Total Price', ]
        ]  # CSV header

        # Add the incoming transactions for this particular object
        incoming_trans = obj.incoming_transactions.all().values_list(
            'id', flat=True)
        transactions = ProductTransaction.objects.filter(
            id__in=incoming_trans
        ).values(
            'id', 'source__company__name', 'destination__company__name', 
            'invoice_number', 'date', 'quality_correction', 
            'product__name', 'quantity', 
            'transaction_payments__currency__name', 'reference', 
            'base_price'
        ).annotate(
            total_price=Sum('transaction_payments__amount')
        )
        
        for transaction in transactions:
            input_variable.append(list(transaction.values()))

        # Create an HTTP response with CSV mime type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; \
            filename="transactions_{obj.pk}.csv"'

        # Write the CSV data to the response
        writer = csv.writer(response)
        writer.writerows(input_variable)

        # Return the response which will trigger the download
        return response


class FarmerConsentAlertView(generics.GenericAPIView):
    """
    API to send alerts to slack when farmer consent is changed through 
    passbook
    """

    permission_classes = (ValidTOTP,)

    @staticmethod
    def _is_valid_farmer_and_consent(farmer_id, consent):
        """Checks farmer and consent are valid or not"""

        if not (farmer_id and consent):
            raise BadRequest(
                "Farmer ID and Consent are required", 
                send_to_sentry=False
            )
        
        try:
            farmer = Farmer.objects.get(id=decode(farmer_id))
        except:
            raise BadRequest("Invalid Farmer", send_to_sentry=False)
        
        if not consent in FarmerConsentStatus.values:
            raise BadRequest("Invalid Consent", send_to_sentry=False)
        
        return farmer
    
    @staticmethod
    def _get_text_message(farmer, consent):
        """Formats text message according to consent"""
        consent_colour = "#28A745" 
        if consent != FarmerConsentStatus.GRANTED:
            consent_colour = "#DC3545"  # Red color if consent is not granted
        
        data = {
            "text": f"{farmer.name}- *{farmer.id}*, consent updated!",
            "attachments": [
                {
                    "text": consent,
                    "color": consent_colour,
                    "fields": [
                        {
                            "value": f"<{f'{settings.TRACE_URL}/djadmin-ff/supply_chains/farmer/?external_id={farmer.id}'}|Edit Farmer Consent - Trace>"
                        },
                        {
                            "value": f"<{f'{settings.ROOT_URL}/admin/supply_chains/farmer/{farmer.id}'}|Edit Farmer Consent - Connect>"
                        }
                    ]
                }
            ]
        }
        return data

    def post(self, request, *args, **kwargs):
        farmer_id = request.data.get("farmer", None)
        consent = request.data.get("consent")

        farmer = self._is_valid_farmer_and_consent(farmer_id, consent)

        data = self._get_text_message(farmer, consent)
        headers = {"Content-Type": "application/json"}
        url = settings.FARMER_CONSENT_WEBHOOK_URL
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            capture_message(
                f"Farmer Consent Alert Failed-{farmer.id}"
            )
        return Response(response.status_code)