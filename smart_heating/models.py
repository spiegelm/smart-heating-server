from django.core import validators
from django.db import models
from abc import ABCMeta, abstractmethod

# Create your models here.


alpha_numeric_validator = validators.RegexValidator(r'^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')
rfid_validator = alpha_numeric_validator

class Model(models.Model):
    __metaclass__ = ABCMeta

    # TODO refactor the models to reuse more code
    # parent = None

    class Meta:
        abstract = True

    def __repr__(self):
        fields_string = ', '.join(['%s:"%s"' % (field.name, getattr(self, field.name)) for field in self._meta.fields])
        return '<%s(%s)>' % (self.__class__._meta.object_name, fields_string)

    def __str__(self):
        return str(self.pk)

    @abstractmethod
    def get_recursive_pks(self):
        """
        Returns a list of primary keys of all recursive parents.
        Used to determine the URL of an object.
        """
        pass


class Residence(Model):
    rfid = models.CharField(primary_key=True, max_length=100, validators=[rfid_validator])

    class Meta:
        ordering = ('rfid',)

    def get_recursive_pks(self):
        pks = [self.pk]
        return pks


class User(Model):
    imei = models.CharField(primary_key=True, max_length=100, validators=[alpha_numeric_validator])
    name = models.CharField(max_length=100)
    residence = models.ForeignKey('Residence', related_name='users')

    class Meta:
        ordering = ('imei',)

    def get_recursive_pks(self):
        pks = self.residence.get_recursive_pks()
        pks.append(self.pk)
        return pks


class Room(Model):
    # id is automatically generated if no other primary_key is defined
    name = models.CharField(max_length=100)
    residence = models.ForeignKey('Residence', related_name='rooms')

    class Meta:
        ordering = ('name',)

    def get_recursive_pks(self):
        pks = self.residence.get_recursive_pks()
        pks.append(self.pk)
        return pks



class Thermostat(Model):
    rfid = models.CharField(primary_key=True, max_length=100, validators=[rfid_validator])
    room = models.ForeignKey('Room', related_name='thermostats')

    class Meta:
        ordering = ('rfid',)

    def get_recursive_pks(self):
        pks = self.room.get_recursive_pks()
        pks.append(self.pk)
        return pks


# TODO use separate primary key and unique_together, as in HeatingTableEntry
class Temperature(Model):
    # TODO test datetime validation
    datetime = models.DateTimeField(primary_key=True)
    value = models.FloatField(validators=[validators.MinValueValidator(5), validators.MaxValueValidator(30)])
    thermostat = models.ForeignKey('Thermostat', related_name='temperatures')

    class Meta:
        ordering = ('datetime',)

    def get_recursive_pks(self):
        pks = self.thermostat.get_recursive_pks()
        assert(self.pk == self.datetime)
        pks.append(self.datetime.isoformat())
        return pks


class ThermostatMetaEntry(Model):

    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    rssi = models.IntegerField(null=True)
    uptime = models.IntegerField(null=True)
    battery = models.IntegerField(null=True)
    thermostat = models.ForeignKey('Thermostat', related_name='meta_entries')

    class Meta:
        unique_together = ('thermostat', 'datetime')
        ordering = ('datetime',)

    def get_recursive_pks(self):
        pks = self.thermostat.get_recursive_pks()
        pks.append(self.pk)
        return pks


class Device(Model):
    __metaclass__ = ABCMeta

    rfid = models.CharField(primary_key=True, max_length=100, validators=[rfid_validator])
    mac = models.CharField(max_length=17, unique=True)

    class Meta:
        abstract = True

    def get_recursive_pks(self):
        return [self.pk]


class RaspberryDevice(Device):

    @property
    def residence(self):
        residences = Residence.objects.filter(rfid=self.rfid)
        assert(0 <= len(residences) <= 1)
        if len(residences) > 0:
            return residences[0]
        else:
            return None

    @property
    def thermostat_devices(self):
        residence = self.residence
        if residence is None:
            return None
        rooms = Room.objects.filter(residence=residence)
        room_pks = [room.pk for room in rooms]
        thermostats = Thermostat.objects.filter(room__in=room_pks)
        thermostat_rfids = [thermostat.rfid for thermostat in thermostats]
        thermostat_devices = ThermostatDevice.objects.filter(rfid__in=thermostat_rfids)
        return thermostat_devices


class ThermostatDevice(Device):

    @property
    def thermostat(self):
        thermostats = Thermostat.objects.filter(rfid=self.rfid)
        assert(0 <= len(thermostats) <= 1)
        if len(thermostats) > 0:
            return thermostats[0]
        else:
            return None


class TimetableEntry(Model):
    __metaclass__ = ABCMeta

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    DAY_IN_WEEK_CHOICES = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    ]

    day = models.CharField(max_length=3, choices=DAY_IN_WEEK_CHOICES)
    time = models.TimeField()

    class Meta:
        abstract = True


class HeatingTableEntry(TimetableEntry):

    class Meta:
        unique_together = ('day', 'time', 'thermostat')
        ordering = ('day', 'time')

    temperature = models.FloatField()
    thermostat = models.ForeignKey(Thermostat, related_name='heating_table_entries')

    def get_recursive_pks(self):
        pks = self.thermostat.get_recursive_pks()
        pks.append(self.pk)
        return pks


class OccupancyPredictionEntry(TimetableEntry):

    class Meta:
        unique_together = ('day', 'time', 'user')
        ordering = ('day', 'time')

    user = models.ForeignKey(User)

    def get_recursive_pks(self):
        pks = self.user.get_recursive_pks()
        pks.append(self.pk)
        return pks
