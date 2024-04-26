from rest_framework.pagination import LimitOffsetPagination
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