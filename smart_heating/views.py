# Create your views here.

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse

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


class TemperatureViewSet(viewsets.ModelViewSet):

    queryset = Temperature.objects.all()
    serializer_class = TemperatureSerializer

    def get_queryset(self):
        residence_pk = self.kwargs.get('residence_pk')
        room_pk = self.kwargs.get('room_pk')
        thermostat_pk = self.kwargs.get('thermostat_pk')
        # check residence, room and thermostat in hierarchy
        get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)
        get_object_or_404(Thermostat.objects.all(), room=room_pk, pk=thermostat_pk)
        return Temperature.objects.filter(thermostat=thermostat_pk)
