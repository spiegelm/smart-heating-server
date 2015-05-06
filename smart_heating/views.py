# Create your views here.

from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
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
        queryset = User.objects.filter(residence=residence_pk)
        return queryset


class RoomViewSet(viewsets.ModelViewSet):

    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_queryset(self):
        residence_pk = self.kwargs.get('residence_pk')
        return Room.objects.filter(residence=residence_pk)


class ThermostatViewSet(viewsets.ModelViewSet):

    queryset = Thermostat.objects.all()
    serializer_class = ThermostatSerializer

    def get_queryset(self, residence_pk, room_pk):
        # check residence and room
        get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)
        return super(ThermostatViewSet, self).get_queryset()

    def list(self, request, residence_pk, room_pk):
        queryset = self.get_queryset(residence_pk, room_pk)
        list = queryset.all().filter(room=room_pk)
        serializer = ThermostatSerializer(list, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, residence_pk, room_pk, pk):
        queryset = self.get_queryset(residence_pk, room_pk)
        # # check residence and room
        # get_object_or_404(Room.objects.all(), residence=residence, pk=room)
        thermostat = get_object_or_404(queryset, pk=pk, room=room_pk)
        serializer = ThermostatSerializer(thermostat, context={'request': request})
        return Response(serializer.data)


from rest_framework import status
import django


class TemperatureViewSet(viewsets.ModelViewSet):

    queryset = Temperature.objects.all()
    serializer_class = TemperatureSerializer

    def get_queryset(self, residence_pk, room_pk, thermostat_pk):
        # check residence, room and thermostat
        get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)
        get_object_or_404(Thermostat.objects.all(), room=room_pk, pk=thermostat_pk)
        return super(TemperatureViewSet, self).get_queryset()

    def list(self, request, residence_pk, room_pk, thermostat_pk):
        queryset = self.get_queryset(residence_pk, room_pk, thermostat_pk)
        list = queryset.all().filter(thermostat=thermostat_pk)
        serializer = TemperatureSerializer(list, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, residence_pk, room_pk, thermostat_pk, pk):
        queryset = self.get_queryset(residence_pk, room_pk, thermostat_pk)
        temperature = get_object_or_404(queryset, pk=pk, thermostat=thermostat_pk)
        serializer = TemperatureSerializer(temperature, context={'request': request})
        return Response(serializer.data)

    # TODO make create (POST) working
    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     data.update(kwargs)
    #     print(data)
    #
    #     serializer = TemperatureSerializer(context={'request': request}, data=data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)