from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from project.pagination import CustomPagination

from smart_heating.serializers import *


class ResidenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows residences to be viewed or edited.
    """
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        residence_pk = self.kwargs['residence_pk']
        get_object_or_404(Residence.objects.all(), pk=residence_pk)
        return User.objects.filter(residence=residence_pk)

    def perform_create(self, serializer):
        # Grab residence from kwargs provided by the router
        residence = Residence.objects.get(pk=self.kwargs.get('residence_pk'))
        # Add residence information to the serializer
        serializer.save(residence=residence)


class RoomViewSet(viewsets.ModelViewSet):

    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_queryset(self):
        residence_pk = self.kwargs.get('residence_pk')
        get_object_or_404(Residence.objects.all(), pk=residence_pk)
        return Room.objects.filter(residence=residence_pk)

    def perform_create(self, serializer):
        # Grab residence from kwargs provided by the router
        residence = Residence.objects.get(pk=self.kwargs.get('residence_pk'))
        # Add residence information to the serializer
        serializer.save(residence=residence)


class ThermostatViewSet(viewsets.ModelViewSet):

    queryset = Thermostat.objects.all()
    serializer_class = ThermostatSerializer

    def get_queryset(self):
        residence_pk = self.kwargs.get('residence_pk')
        room_pk = self.kwargs.get('room_pk')
        get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)
        return Thermostat.objects.filter(room=room_pk)

    def perform_create(self, serializer):
        # Grab room from kwargs provided by the router
        room = Room.objects.get(pk=self.kwargs.get('room_pk'))
        # Add residence information to the serializer
        serializer.save(room=room)


class TemperatureViewSet(viewsets.ModelViewSet):

    queryset = Temperature.objects.all()
    serializer_class = TemperatureSerializer
    pagination_class = CustomPagination

    # Allow dots in the lookup value
    # The datetime primary key uses a dot to format milliseconds
    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        residence_pk = self.kwargs.get('residence_pk')
        room_pk = self.kwargs.get('room_pk')
        thermostat_pk = self.kwargs.get('thermostat_pk')
        # check residence, room and thermostat in hierarchy
        get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)
        get_object_or_404(Thermostat.objects.all(), room=room_pk, pk=thermostat_pk)
        return Temperature.objects.filter(thermostat=thermostat_pk)

    def perform_create(self, serializer):
        # Grab thermostat from kwargs provided by the router
        thermostat = Thermostat.objects.get(pk=self.kwargs.get('thermostat_pk'))
        # Add residence information to the serializer
        serializer.save(thermostat=thermostat)

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request, *args, **kwargs):
        temperatures = self.get_queryset().order_by('-datetime')
        if len(temperatures) == 0:
            raise Http404('There are no temperatures.')
        latest_temperature = temperatures[0]
        return Response(self.get_serializer(latest_temperature).data)


class DeviceLookupMixin(viewsets.ModelViewSet):

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

    queryset = RaspberryDevice.objects.all()
    serializer_class = RaspberryDeviceSerializer


class ThermostatDeviceViewSet(DeviceLookupMixin,
                              viewsets.ModelViewSet):

    queryset = ThermostatDevice.objects.all()
    serializer_class = ThermostatDeviceSerializer
