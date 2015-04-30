from django.forms import widgets
from rest_framework import serializers
from smart_heating import relations
from smart_heating.models import *


class ResidenceSerializer(serializers.HyperlinkedModelSerializer):
    rooms = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # TODO reference rooms per URL using a custom Field
    # http://www.django-rest-framework.org/api-guide/relations/#advanced-hyperlinked-fields
    # rooms = serializers.HyperlinkedRelatedField(many=True, view_name='room-detail',
    #                                             lookup_url_kwarg='residence', read_only=True)
    room_base_url = serializers.HyperlinkedIdentityField(view_name='room-list', lookup_url_kwarg='residence_pk')

    class Meta:
        model = Residence
        fields = ('rfid', 'url', 'room_base_url', 'rooms', 'users')


# TODO use a HyperlinkedModelSerializer
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('imei', 'name', 'residence')


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='room-detail', read_only=True)
    thermostats = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'url', 'name', 'residence', 'thermostats')


# TODO use a HyperlinkedModelSerializer
class ThermostatSerializer(serializers.ModelSerializer):
    temperatures = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Thermostat
        fields = ('rfid', 'room', 'temperatures')


# TODO use a HyperlinkedModelSerializer
class TemperatureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Temperature
        fields = ('datetime', 'value', 'thermostat')
