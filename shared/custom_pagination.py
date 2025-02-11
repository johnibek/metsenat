from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    'previous': self.get_previous_link(),
                    'next': self.get_next_link()
                },
                "count": self.page.paginator.count,
                "result": data
            }
        )
