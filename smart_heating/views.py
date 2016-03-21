"""
Copyright 2016 Michael Spiegel, Wilhelm Kleiminger

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, renderers, mixins
from rest_framework.decorators import list_route

from smart_heating.pagination import *
from smart_heating.serializers import *


class HierarchicalModelHelper:
    """
    Helper class for hierarchical models.
    Provides access to the often used residence, room and thermostat objects.
    """
    def get_residence(self):
        return get_object_or_404(Residence.objects.all(), pk=self.kwargs['residence_pk'])

    def get_room(self):
        residence_pk = self.kwargs.get('residence_pk')
        room_pk = self.kwargs.get('room_pk')
        return get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)

    def get_thermostat(self):
        room_pk = self.kwargs.get('room_pk')
        thermostat_pk = self.kwargs.get('thermostat_pk')
        return get_object_or_404(Thermostat.objects.all(), room=room_pk, pk=thermostat_pk)

    @abstractmethod
    def get_parent(self):
        """
        Returns a dictionary of {parent_name: parent_model_instance}.
        """
        pass

    @abstractmethod
    def check_hierarchy(self):
        """
        Checks if the URL arguments match the parents of the queried model.
        """
        pass

    def get_queryset(self):
        self.check_hierarchy()
        return self.queryset.filter(**self.get_parent())

    def get_serializer_extra_data(self):
        return self.get_parent()


class ProtectedModelViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet,
                            HierarchicalModelHelper):
    """
    A viewset that provides default `create()`, `retrieve()`,
    `destroy()` and `list()` actions.
    """
    pass


class HierarchicalModelViewSet(HierarchicalModelHelper,
                               viewsets.ModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context['extra_data'] = self.get_serializer_extra_data()
        return context


class ResidenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that represents residences.

    Each residence corresponds to an installed local communication gateway, i.e. a Raspberry Pi.
    See the <a href="/device/raspberry/">/device/raspberry/</a> endpoint for more information.
    """
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer


class UserViewSet(HierarchicalModelViewSet):
    """
    API endpoint that represents users.

    Each user is identified by her IMEI and is associated to exactly one residence.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_parent(self):
        return {'residence': self.get_residence()}


class RoomViewSet(HierarchicalModelViewSet):
    """
    API endpoint that represents rooms.

    A room is part of a residence and is used to group thermostats.
    """

    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_parent(self):
        return {'residence': self.get_residence()}


class ThermostatViewSet(HierarchicalModelViewSet):
    """
    API endpoint that represents thermostats.

    Contains the temperature values, the heating table and other meta data.
    See the <a href="/device/thermostat/">/device/thermostat/</a> endpoint for more information.
    """

    queryset = Thermostat.objects.all()
    serializer_class = ThermostatSerializer

    def get_parent(self):
        return {'room': self.get_room()}


class TemperatureViewSet(HierarchicalModelViewSet):
    """
    API endpoint that represents a thermostat's temperatures.

    Offers pagination and custom views for the latest temperature measurement
    and a chart to review current and historic values.
    """

    queryset = Temperature.objects.all()
    serializer_class = TemperatureSerializer

    # Allow dots in the lookup value. The datetime primary key uses a dot to represent milliseconds
    lookup_value_regex = '[^/]+'

    def get_parent(self):
        return {'thermostat': self.get_thermostat()}

    def check_hierarchy(self):
        self.get_room()

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request, *args, **kwargs):
        temperatures = self.get_queryset().order_by('-datetime')
        if len(temperatures) == 0:
            raise Http404('There are no temperatures.')
        latest_temperature = temperatures[0]
        return Response(self.get_serializer(latest_temperature).data)

    @list_route(methods=['get'], url_path='chart', renderer_classes=[renderers.TemplateHTMLRenderer])
    def chart(self, request, *args, **kwargs):
        temperatures = self.get_queryset()
        print(temperatures)
        context = {
            'temperatures': [[int(t.datetime.timestamp() * 1000), t.value] for t in temperatures],
            'room': self.get_room(),
            'thermostat': self.get_thermostat()
        }
        return render(request, 'smart_heating/temperature_chart.html', context)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        # Override the paginator property to inject the kwargs to the paginator. This is required
        # to generate the latest_temperature_url.
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = TemperaturePagination(kwargs=self.kwargs)
        return self._paginator


class ThermostatMetaEntryViewSet(HierarchicalModelViewSet):
    """
    API endpoint that represents a time depending meta information about thermostats.

    A meta entry consists of the received signal strength, up-time, battery level
    and an associated timestamp. This data can be used to identify issues regarding the
    thermostat devices such as wireless connection problems or drained batteries.
    """

    queryset = ThermostatMetaEntry.objects.all()
    serializer_class = ThermostatMetaEntrySerializer

    def get_parent(self):
        return {'thermostat': self.get_thermostat()}

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request, *args, **kwargs):
        meta_entries = self.get_queryset().order_by('-datetime')
        if len(meta_entries) == 0:
            raise Http404('There are no meta entries.')
        latest_temperature = meta_entries[0]
        return Response(self.get_serializer(latest_temperature).data)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        # Override the paginator property to inject the kwargs to the paginator. This is required
        # to generate the url for the latest entry.
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = ThermostatMetaEntriesPagination(kwargs=self.kwargs)
        return self._paginator


class HeatingTableEntryViewSet(HierarchicalModelViewSet):
    """
    API endpoint that represents the thermostat's associated temperature schedule.

    The heating table is responsible for mapping each day and time in a week to a target temperature.
    It's a periodic schedule repeating each week.
    The first day of a week is 0 (Monday) and the last day of a week is 6 (Sunday).
    """

    queryset = HeatingTableEntry.objects.all()
    serializer_class = HeatingTableEntrySerializer

    def get_parent(self):
        return {'thermostat': self.get_thermostat()}

    def check_hierarchy(self):
        # Check residence, room and thermostat in hierarchy
        self.get_room()  # This includes the residence check
        self.get_thermostat()


class DeviceLookupMixin(viewsets.ModelViewSet):
    """
    Provides a list route to lookup a device by its MAC address.
    """
    @list_route(methods=['get'], url_path='lookup')
    def lookup(self, request, *args, **kwargs):
        mac = request.GET.get('mac')
        if mac is None:
            return Response(status=400, data={'mac': ['This field is required']})
        device = get_object_or_404(self.get_queryset(), mac=mac)
        serializer = self.get_serializer(device)
        return Response(serializer.data)


class RaspberryDeviceViewSet(DeviceLookupMixin,
                             viewsets.ModelViewSet):
    """
    API endpoint that links the MAC address of local communication gateways (Raspberry Pi) with their RFID tag.

    Each Raspberry Pi corresponds to a residence.
    This endpoint allows a Raspberry Pi to retrieve its associated RFID tag based on its Ethernet MAC address.
    As soon as the user registers her Raspberry Pi it can query its associated thermostats.
    This data must be provided before deployment.
    """

    queryset = RaspberryDevice.objects.all()
    serializer_class = RaspberryDeviceSerializer


class ThermostatDeviceViewSet(DeviceLookupMixin,
                              viewsets.ModelViewSet):
    """
    API endpoint that links the MAC address of wireless thermostats with their RFID tag.

    This data must be provided before deployment.
    """

    queryset = ThermostatDevice.objects.all()
    serializer_class = ThermostatDeviceSerializer
