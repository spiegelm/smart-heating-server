from rest_framework import serializers
from rest_framework.fields import empty
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
    rooms_url = serializers.HyperlinkedIdentityField(view_name='room-list', lookup_url_kwarg='residence_pk')
    users_url = serializers.HyperlinkedIdentityField(view_name='user-list', lookup_url_kwarg='residence_pk')

    class Meta:
        model = Residence
        fields = ('rfid', 'url', 'rooms_url', 'users_url')


class UserSerializer(HierarchicalSerializer):

    url = relations.HierarchicalHyperlinkedIdentityField(view_name='user-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('imei', 'url', 'name', 'residence')


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='room-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)
    thermostats_url = relations.HierarchicalHyperlinkedIdentityField(source='thermostats', view_name='thermostat-list',
                                                                     read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'url', 'name', 'residence', 'thermostats_url')


class ThermostatSerializer(serializers.HyperlinkedModelSerializer):
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
        fields = ('rfid', 'url', 'room', 'temperatures_url', 'meta_entries_url', 'heating_table_url')


class SimpleThermostatSerializer(ThermostatSerializer):
    """
    For a simplified representation. Includes only the url field.
    """
    class Meta:
        model = Thermostat
        fields = ('url',)


class HeatingTableEntrySerializer(HierarchicalSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='heatingtableentry-detail', read_only=True)
    thermostat = SimpleThermostatSerializer(read_only=True)

    class Meta:
        model = HeatingTableEntry
        fields = ('id', 'url', 'day', 'time', 'temperature', 'thermostat')
        validators = [UniqueTogetherValidator(queryset=model.objects.all(),
                                              fields=('day', 'time', 'thermostat'))]
        # validators = [UniqueTogetherValidator(queryset=model.objects.all(),
        #                                       fields=model._meta.unique_together)]


class TemperatureSerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='temperature-detail', read_only=True)
    # Use the simplified serializer for a smaller payload size
    thermostat = SimpleThermostatSerializer(read_only=True)

    class Meta:
        model = Temperature
        fields = ('datetime', 'url', 'value', 'thermostat')


class ThermostatMetaEntrySerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='thermostatmetaentry-detail', read_only=True)

    class Meta:
        model = ThermostatMetaEntry
        fields = ('id', 'url', 'datetime', 'rssi', 'uptime', 'battery')
        extra_kwargs = {'thermostat': {}}


class ThermostatDeviceSerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='thermostatdevice-detail', read_only=True)
    thermostat = ThermostatSerializer(read_only=True)
    # TODO validate MAC field

    class Meta:
        model = ThermostatDevice
        fields = ('rfid', 'mac', 'url', 'thermostat')


class RaspberryDeviceSerializer(serializers.HyperlinkedModelSerializer):
    url = relations.HierarchicalHyperlinkedIdentityField(view_name='raspberrydevice-detail', read_only=True)
    residence = ResidenceSerializer(read_only=True)
    thermostat_devices = ThermostatDeviceSerializer(read_only=True, many=True)
    # TODO validate MAC field

    class Meta:
        model = RaspberryDevice
        fields = ('rfid', 'mac', 'url', 'residence', 'thermostat_devices')
