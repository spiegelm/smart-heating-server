from rest_framework import status
from rest_framework.test import APITestCase
from smart_heating import models


class ViewRootTestCase(APITestCase):

    def test_root_contains_residence_url(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,
                         {'residence': 'http://testserver/residence/'})


class ViewResidenceTestCase(APITestCase):

    def test_list_residences_empty(self):
        response = self.client.get('/residence/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_single_residence(self):
        residence = models.Residence.objects.create(rfid='3')
        response = self.client.get('/residence/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        data = response.data[0]
        self.assertEqual(data.get('rfid'), '3', 'RFID')
        self.assertEqual(data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(data.get('room_base_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(data.get('rooms'), [])

    def test_get_residence_without_rooms(self):
        residence = models.Residence.objects.create(rfid='3')
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('rfid'), '3', 'RFID')
        self.assertEqual(response.data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(response.data.get('room_base_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(response.data.get('rooms'), [])

    def test_get_residence_with_rooms(self):
        residence = models.Residence.objects.create(rfid='3')
        room1 = models.Room.objects.create(residence=residence)
        room2 = models.Room.objects.create(residence=residence)
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('rfid'), '3', 'RFID')
        self.assertEqual(response.data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(response.data.get('room_base_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(response.data.get('rooms'), [room1.pk, room2.pk])

    def test_get_residence_404(self):
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_residence(self):
        response = self.client.post('/residence/', {'rfid': '3'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('rfid'), '3')

        queryset = models.Residence.objects.all().filter(rfid='3')
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].rfid, '3')

    def test_update_residence(self):
        residence = models.Residence.objects.create(rfid='3')

        response = self.client.put('/residence/3/', {'rfid': '42'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        queryset = models.Residence.objects.all().filter(rfid='42')
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].rfid, '42')

    def test_destroy_residence(self):
        residence = models.Residence.objects.create(rfid='3')
        queryset = models.Residence.objects.all().filter(rfid='3')
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].rfid, '3')

        response = self.client.delete('/residence/3/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        queryset = models.Residence.objects.all().filter(rfid='3')
        self.assertEqual(len(queryset), 0)


class ViewRoomTestCase(APITestCase):

    residence = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')

    def test_list_rooms_empty(self):
        response = self.client.get('/residence/3/room/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_single_room(self):
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')

        response = self.client.get('/residence/3/room/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('name'), 'Dining Room')
        self.assertEqual(response.data[0].get('residence'), 'http://testserver/residence/3/')

    def test_get_room(self):
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')

        response = self.client.get('/residence/3/room/%s/' % room.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), room.pk)
        self.assertEqual(response.data.get('url'), 'http://testserver/residence/3/room/%s/' % room.pk)
        self.assertEqual(response.data.get('name'), 'Dining Room')
        self.assertEqual(response.data.get('residence'), 'http://testserver/residence/3/')

    def test_get_room_shows_thermostats(self):
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')
        thermostat = models.Thermostat.objects.create(room=room, rfid='thermoX')

        response = self.client.get('/residence/3/room/%s/' % room.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('thermostats_pk'), ['thermoX'])

    # TODO add test for PUT and POST


class ViewThermostatTestCase(APITestCase):

    residence = None
    room = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')
        self.room = models.Room.objects.create(residence=self.residence)

    def test_get_empty_thermostat_list(self):
        response = self.client.get('/residence/3/room/%s/thermostat/' % self.room.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
