from django.db import models

# Create your models here.


class Residence(models.Model):
    rfid = models.CharField(primary_key=True, max_length=100)

    class Meta:
        ordering = ('rfid',)

    def __str__(self):
        """
        Used to generate the url
        """
        return self.rfid

    def get_recursive_pks(self):
        """
        Returns a list of primary keys of all recursive parents.
        Used to determine the URL of an object.
        """
        pks = [self.pk]
        return pks



class User(models.Model):
    imei = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    residence = models.ForeignKey('Residence')

    class Meta:
        ordering = ('imei',)


class Room(models.Model):
    # id is automatically generated
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    residence = models.ForeignKey('Residence', related_name='rooms')

    class Meta:
        ordering = ('name',)

    def get_recursive_pks(self):
        """
        Returns a list of primary keys of all recursive parents.
        Used to determine the URL of an object.
        """
        pks = self.residence.get_recursive_pks()
        pks.append(self.pk)
        return pks


# TODO model the heating table
# class HeatingTable(models.Model):


class Thermostat(models.Model):
    rfid = models.CharField(primary_key=True, max_length=100)
    room = models.ForeignKey('Room', related_name='thermostats')

    class Meta:
        ordering = ('rfid',)


class Temperature(models.Model):
    datetime = models.DateTimeField(primary_key=True)
    value = models.FloatField()
    thermostat = models.ForeignKey('Thermostat', related_name='temperatures')

    class Meta:
        ordering = ('datetime',)