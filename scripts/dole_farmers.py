import numpy as np
import pandas as pd
from django.apps import apps
from django.db.models import Count
from django.db.models import Sum

from base.authentication.session import set_to_local
from v1.supply_chains.serializers import FarmerSerializer
from v1.transactions.serializers import ProductTransactionSerializer


COMPANY_NAME = "Dole"
PACKHOUSE_NAME = "Packhouse"
EXPORT_COMPANY_NAME = "SRCC"

CompanyModel = apps.get_model("supply_chains", "Company")
ProductTransactionModel = apps.get_model("transactions", "ProductTransaction")


def load_file(sheet_name, header=0):
    """Load."""
    return pd.read_excel(
        "fixtures/test_files/dole.xlsx", sheet_name=sheet_name, header=header
    )


def farmer_headers():
    """Returns."""
    return [
        "first_name",
        "last_name",
        "identification_no",
        "street",
        "city",
        "province",
        "zipcode",
        "country",
        "latitude",
        "longitude",
        "phone",
        "gender",
        "date_of_birth",
        "house_hold_size",
        "description",
        "long_description",
    ]


def transaction_headers():
    """Transactional headers."""
    return ["source", "reference", "date", "quantity"]


def get_packhouse():
    """get the packhouse."""
    try:
        return CompanyModel.objects.get(name__icontains=PACKHOUSE_NAME)
    except CompanyModel.DoesNotExist:
        raise ValueError(f"Company {PACKHOUSE_NAME} not found")


def get_srcc():
    """Returns the srcc."""
    try:
        return CompanyModel.objects.get(name__icontains=EXPORT_COMPANY_NAME)
    except CompanyModel.DoesNotExist:
        raise ValueError(f"Company {EXPORT_COMPANY_NAME} not found")


def farmer_identification_id_map(company):
    """Returns."""
    return dict(
        company.entity_supplers.values_list("farmer__identification_no", "pk")
    )


def upload_dole_farmers():
    """Upload."""
    df = load_file("Farmer Details")
    buyer = get_packhouse()
    set_to_local("user_id", buyer.members.first().id)
    set_to_local("entity_id", buyer.pk)
    df.columns = farmer_headers()
    df["first_name"] = df["first_name"].fillna(df["identification_no"])
    df["last_name"] = df["last_name"].apply(lambda x: f"({x})")
    df["buyer"] = buyer.id.hashid
    df = df.replace([np.nan], [None])
    serializer = FarmerSerializer(data=df.to_dict(orient="records"), many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def upload_farmer_transactions():
    """Upload."""
    df = load_file("Transaction data till dole", header=1)
    df = df.iloc[:, [0, 4, 5, 6]]
    df.columns = transaction_headers()
    buyer = get_packhouse()
    set_to_local("user_id", buyer.members.first().id)
    set_to_local("entity_id", buyer.pk)
    source_map = farmer_identification_id_map(buyer)
    company_product = buyer.company_products.last()
    if not company_product:
        raise ValueError("No company product")
    df["source"] = df["source"].apply(lambda x: source_map.get(str(x), ""))
    df["date"] = df["date"].apply(lambda x: int(x.timestamp()))
    df["destination"] = buyer.id.hashid
    df["product"] = company_product.product.id.hashid
    df["amount"] = 0.0
    df["currency"] = buyer.currency.pk.hashid if buyer.currency else "EUR"
    df = df.replace([np.nan], [None])
    serializer = ProductTransactionSerializer(
        data=df.to_dict(orient="records"), many=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()


def reference_batch_map():
    """Reference."""
    df = load_file("Transaction data till dole", header=1)
    df = df.iloc[:, [4, 13]]
    df.columns = ["reference", "batch"]
    return df.groupby("batch")["reference"]


def merge_pallets():
    """Merge pallets."""
    company = get_packhouse()
    set_to_local("user_id", company.members.first().id)
    set_to_local("entity_id", company.pk)
    company_product = company.company_products.first()
    if not company_product:
        raise ValueError("No company product")
    transactions = ProductTransactionModel.objects.annotate(
        total_children=Count("children")
    ).filter(pk__in=company.incoming_transactions.only("id"), total_children=0)
    references = (
        ProductTransactionModel.objects.filter(pk__in=transactions)
        .values_list("reference", flat=True)
        .order_by("reference")
        .distinct("reference")
    )
    data = []
    for reference in references:
        parents = transactions.filter(reference=reference)
        data.append(
            {
                "parents": parents.values_list("id", flat=True),
                "date": int(parents.last().date.timestamp()),
                "reference": reference,
                "source": company.pk,
                "destination": company.pk,
                "amount": 0.0,
                "quantity": parents.aggregate(Sum("quantity"))[
                    "quantity__sum"
                ],
                "product": company_product.product.id.hashid,
                "currency": (
                    company.currency.pk.hashid if company.currency else "EUR"
                ),
            }
        )
    serializer = ProductTransactionSerializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def send_pallets():
    """Sent pallets."""
    company = get_packhouse()
    set_to_local("user_id", company.members.first().id)
    set_to_local("entity_id", company.pk)
    company_product = company.company_products.first()
    if not company_product:
        raise ValueError("No company product")
    transactions = ProductTransactionModel.objects.annotate(
        total_children=Count("children")
    ).filter(source=company, destination=company, total_children=0)

    data = {
        "parents": transactions.values_list("id", flat=True),
        "date": int(transactions.last().date.timestamp()),
        "source": company.pk,
        "destination": company.buyer.pk,
        "amount": 0.0,
        "quantity": transactions.aggregate(Sum("quantity"))["quantity__sum"],
        "product": company_product.product.id.hashid,
        "currency": (
            company.currency.pk.hashid if company.currency else "EUR"
        ),
        "send_seperately": True,
    }

    serializer = ProductTransactionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def sent_again():
    """Merge batches."""
    company = get_srcc()
    set_to_local("user_id", company.members.first().id)
    set_to_local("entity_id", company.pk)
    company_product = company.company_products.first()
    if not company_product:
        raise ValueError("No company product")
    transactions = ProductTransactionModel.objects.annotate(
        total_children=Count("children")
    ).filter(total_children=0, destination=company)
    data = {
        "parents": transactions.values_list("id", flat=True),
        "date": int(transactions.last().date.timestamp()),
        "source": company.pk,
        "destination": company.buyer.pk,
        "amount": 0.0,
        "quantity": transactions.aggregate(Sum("quantity"))["quantity__sum"],
        "product": company_product.product.id.hashid,
        "currency": (
            company.currency.pk.hashid if company.currency else "EUR"
        ),
        "send_seperately": True,
    }

    serializer = ProductTransactionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def run():
    """Run."""
    pass
