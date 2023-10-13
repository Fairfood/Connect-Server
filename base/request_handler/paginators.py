from rest_framework import pagination


class LargePaginator(pagination.PageNumberPagination):
    """Custom paginator for large page sizes.

    This class extends the PageNumberPagination class from DRF to
    provide a custom paginator with a large default page size of 999
    items.
    """

    page_size = 999
