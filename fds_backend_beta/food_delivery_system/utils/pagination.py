from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """Custom pagination with page size and metadata customization."""

    page_size = 10  # Default page size
    page_size_query_param = 'page_size'  # Custom page size
    max_page_size = 100  # Limit maximum page size

    def get_paginated_response(self, data):
        """Customize the paginated response."""
        return Response({
            'total_pages': self.page.paginator.num_pages,
            'total_objects': self.page.paginator.count,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,  # Actual paginated data
        })

