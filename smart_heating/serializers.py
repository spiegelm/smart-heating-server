from django.forms import widgets
from rest_framework import serializers
from smart_heating import relations
from smart_heating.models import *


class ResidenceSerializer(serializers.HyperlinkedModelSerializer):
    rooms_url = serializers.HyperlinkedIdentityField(view_name='room-list', lookup_url_kwarg='residence_pk')
    users_url = serializers.HyperlinkedIdentityField(view_name='user-list', lookup_url_kwarg='residence_pk')

    class Meta:
        model = Residence
        fields = ('rfid', 'url', 'rooms_url', 'users_url')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='user-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('imei', 'url', 'name', 'residence')


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='room-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)
    thermostats_url = relations.HierarchicalHyperlinkedIdentityField(source='thermostats', view_name='thermostat-list', read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'url', 'name', 'residence', 'thermostats_url')


class ThermostatSerializer(serializers.HyperlinkedModelSerializer):
    room_pk = serializers.PrimaryKeyRelatedField(source='room', queryset=Room.objects.all())
    temperatures_pk = serializers.PrimaryKeyRelatedField(source='temperatures', many=True, read_only=True)

    class Meta:
        model = Thermostat
        fields = ('rfid', 'room_pk', 'temperatures_pk')


# TODO use a HyperlinkedModelSerializer
class TemperatureSerializer(serializers.ModelSerializer):
    thermostat_pk = serializers.PrimaryKeyRelatedField(source='thermostat', queryset=Thermostat.objects.all())

    class Meta:
        model = Temperature
        fields = ('datetime', 'value', 'thermostat_pk')
