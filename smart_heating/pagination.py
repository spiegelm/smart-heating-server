from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.reverse import reverse


class TemperaturePagination(pagination.LimitOffsetPagination):

    default_limit = 100

    def __init__(self, kwargs):
        self.latest_temperature_url = None
        self.chart_url = None
        self.kwargs = kwargs

    def paginate_queryset(self, queryset, request, view=None):
        self.latest_temperature_url = reverse('temperature-latest', kwargs=self.kwargs, request=request)
        self.chart_url = reverse('temperature-chart', kwargs=self.kwargs, request=request)
        return super(TemperaturePagination, self).paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next_url', self.get_next_link()),
            ('previous_url', self.get_previous_link()),
            ('latest_temperature_url', self.latest_temperature_url),
            ('chart_url', self.chart_url),
            ('results', data)
        ]))
