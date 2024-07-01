from rest_framework.pagination import LimitOffsetPagination , PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class CustomPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data['data']),
            ('message', data['message']),
            ('status', data['res_status']),
            ('code', data['code'])
        ]))

# its just for information how to use PageNumberPagination
class CustomPaginationnnnn(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total_results": self.page.paginator.count,
                "page_size": self.page_size,
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )
