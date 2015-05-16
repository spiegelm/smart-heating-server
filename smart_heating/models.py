from django.db import models
from abc import ABCMeta, abstractmethod

# Create your models here.


class Model(models.Model):
    __metaclass__ = ABCMeta

    # TODO refactor the models to reuse more code
    # parent = None

    class Meta:
        abstract = True

    @abstractmethod
    def get_recursive_pks(self):
        """
        Returns a list of primary keys of all recursive parents.
        Used to determine the URL of an object.
        """
        pass


class Residence(Model):
    rfid = models.CharField(primary_key=True, max_length=100)

    class Meta:
        ordering = ('rfid',)

    def __str__(self):
        """
        Used to generate the url
        """
        return self.rfid

    def get_recursive_pks(self):
        pks = [self.pk]
        return pks


class User(Model):
    imei = models.CharField(primary_key=True, max_length=100)
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


# TODO model the heating table
# class HeatingTable(models.Model):


class Thermostat(Model):
    rfid = models.CharField(primary_key=True, max_length=100)
    room = models.ForeignKey('Room', related_name='thermostats')

    class Meta:
        ordering = ('rfid',)

    def get_recursive_pks(self):
        pks = self.room.get_recursive_pks()
        pks.append(self.pk)
        return pks


class Temperature(Model):
    datetime = models.DateTimeField(primary_key=True)
    value = models.FloatField()
    thermostat = models.ForeignKey('Thermostat', related_name='temperatures')

    class Meta:
        ordering = ('-datetime',)

    def get_recursive_pks(self):
        pks = self.thermostat.get_recursive_pks()
        assert(self.pk == self.datetime)
        pks.append(self.datetime.isoformat())
        return pks


class Device(Model):
    __metaclass__ = ABCMeta

    rfid = models.CharField(primary_key=True, max_length=100)
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


class ThermostatDevice(Device):

    @property
    def thermostat(self):
        thermostats = Thermostat.objects.filter(rfid=self.rfid)
        assert(0 <= len(thermostats) <= 1)
        if len(thermostats) > 0:
            return thermostats[0]
        else:
            return None
