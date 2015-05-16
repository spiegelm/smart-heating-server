from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.LimitOffsetPagination):

    default_limit = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next_url', self.get_next_link()),
            ('previous_url', self.get_previous_link()),
            ('results', data)
        ]))
