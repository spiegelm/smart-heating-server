from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.reverse import reverse


class BasePagination(pagination.LimitOffsetPagination):

    default_limit = 100

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def get_paginated_response(self, data):
        # Prepended meta data
        response_data = OrderedDict([
            ('count', self.count),
            ('next_url', self.get_next_link()),
            ('previous_url', self.get_previous_link())
        ])
        # Custom data
        response_data.update(self.get_custom_pagination_response_data(data))
        # Appended meta data
        response_data.update(OrderedDict([
            ('results', data)
        ]))
        return Response(response_data)

    def get_custom_pagination_response_data(self, data):
        """Override this method in a custom pagination sub class"""
        return OrderedDict()

class TemperaturePagination(BasePagination):

    def __init__(self, kwargs):
        self.latest_temperature_url = None
        self.chart_url = None
        super(TemperaturePagination, self).__init__(kwargs)

    def paginate_queryset(self, queryset, request, view=None):
        self.latest_temperature_url = reverse('temperature-latest', kwargs=self.kwargs, request=request)
        self.chart_url = reverse('temperature-chart', kwargs=self.kwargs, request=request)
        return super(TemperaturePagination, self).paginate_queryset(queryset, request, view)

    def get_custom_pagination_response_data(self, data):
        return OrderedDict([
            ('latest_temperature_url', self.latest_temperature_url),
            ('chart_url', self.chart_url)
        ])

class ThermostatMetaEntriesPagination(BasePagination):

    def __init__(self, kwargs):
        self.latest_entry_url = None
        super(ThermostatMetaEntriesPagination, self).__init__(kwargs)

    def paginate_queryset(self, queryset, request, view=None):
        self.latest_entry_url = reverse('thermostatmetaentry-latest', kwargs=self.kwargs, request=request)
        return super(ThermostatMetaEntriesPagination, self).paginate_queryset(queryset, request, view)

    def get_custom_pagination_response_data(self, data):
        return OrderedDict([
            ('latest_entry_url', self.latest_entry_url),
        ])
