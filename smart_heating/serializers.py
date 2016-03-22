from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from smart_heating import relations
from smart_heating.models import *


class HierarchicalSerializer(serializers.HyperlinkedModelSerializer):
    """
    Retrieves extra data from the context and includes it to the internal value,
    as if it was included in the passed data for .create(), .update(), etc.
    """

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        ret.update(self.context.get('extra_data'))
        return ret


class ResidenceSerializer(serializers.HyperlinkedModelSerializer):
    """
    Converts a residence object to its string representation and vice versa.
    """
    rooms_url = serializers.HyperlinkedIdentityField(view_name='room-list', lookup_url_kwarg='residence_pk')
    users_url = serializers.HyperlinkedIdentityField(view_name='user-list', lookup_url_kwarg='residence_pk')

    class Meta:
        model = Residence
        fields = ('rfid', 'url', 'rooms_url', 'users_url')


class UserSerializer(HierarchicalSerializer):
    """
    Converts a user object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='user-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('imei', 'url', 'name', 'residence')


class RoomSerializer(HierarchicalSerializer):
    """
    Converts a room object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='room-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)
    thermostats_url = relations.HierarchicalHyperlinkedIdentityField(source='thermostats', view_name='thermostat-list',
                                                                     read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'url', 'name', 'residence', 'thermostats_url')


class ThermostatSerializer(HierarchicalSerializer):
    """
    Converts a thermostat object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='thermostat-detail', read_only=True)
    room = RoomSerializer(read_only=True)
    temperatures_url = relations.HierarchicalHyperlinkedIdentityField(source='temperatures',
                                                                      view_name='temperature-list', read_only=True)
    meta_entries_url = relations.HierarchicalHyperlinkedIdentityField(source='meta_entries',
                                                                      view_name='thermostatmetaentry-list',
                                                                      read_only=True)
    heating_table_url = relations.HierarchicalHyperlinkedIdentityField(source='heating_table_entries',
                                                                       view_name='heatingtableentry-list',
                                                                       read_only=True)

    class Meta:
        model = Thermostat
        fields = ('rfid', 'url', 'name', 'room', 'temperatures_url', 'meta_entries_url', 'heating_table_url')


class SimpleThermostatSerializer(ThermostatSerializer):
    """
    Converts a thermostat object to a simplified and most lightweight representation and vice versa.

    Includes only the url field.
    """

    class Meta:
        model = Thermostat
        fields = ('url',)


class HeatingTableEntrySerializer(HierarchicalSerializer):
    """
    Converts a heating table entry object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='heatingtableentry-detail', read_only=True)
    thermostat = SimpleThermostatSerializer(read_only=True)

    class Meta:
        model = HeatingTableEntry
        fields = ('id', 'url', 'day', 'time', 'temperature', 'thermostat')
        validators = [UniqueTogetherValidator(queryset=model.objects.all(),
                                              fields=('day', 'time', 'thermostat'))]


class TemperatureSerializer(HierarchicalSerializer):
    """
    Converts a temperature entry object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='temperature-detail', read_only=True)
    # Use the simplified serializer for a smaller payload size
    thermostat = SimpleThermostatSerializer(read_only=True)

    class Meta:
        model = Temperature
        fields = ('datetime', 'url', 'value', 'thermostat')


class ThermostatMetaEntrySerializer(HierarchicalSerializer):
    """
    Converts a thermostat meta entry object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='thermostatmetaentry-detail', read_only=True)

    class Meta:
        model = ThermostatMetaEntry
        fields = ('id', 'url', 'datetime', 'rssi', 'uptime', 'battery')
        extra_kwargs = {'thermostat': {}}


class ThermostatDeviceSerializer(serializers.HyperlinkedModelSerializer):
    """
    Converts a thermostat device object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='thermostatdevice-detail', read_only=True)
    thermostat = ThermostatSerializer(read_only=True)

    class Meta:
        model = ThermostatDevice
        fields = ('rfid', 'mac', 'url', 'thermostat')


class RaspberryDeviceSerializer(serializers.HyperlinkedModelSerializer):
    """
    Converts a Raspberry Pi device object to its string representation and vice versa.
    """
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='raspberrydevice-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)
    thermostat_devices = ThermostatDeviceSerializer(read_only=True, many=True)

    class Meta:
        model = RaspberryDevice
        fields = ('rfid', 'mac', 'url', 'residence', 'thermostat_devices')
