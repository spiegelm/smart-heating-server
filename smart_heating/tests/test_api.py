from rest_framework import status
from rest_framework.test import APITestCase
from smart_heating import models


class ViewRootTestCase(APITestCase):

    def test_root_contains_residence_url(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('residence'), 'http://testserver/residence/')


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
        self.assertEqual(response.data[0].get('rfid'), '3', 'RFID')
        self.assertEqual(response.data[0].get('url'), 'http://testserver/residence/3/')
        self.assertEqual(response.data[0].get('rooms_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(response.data[0].get('users_url'), 'http://testserver/residence/3/user/')

    def test_get_residence_without_rooms(self):
        residence = models.Residence.objects.create(rfid='3')
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('rfid'), '3', 'RFID')
        self.assertEqual(response.data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(response.data.get('rooms_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(response.data.get('users_url'), 'http://testserver/residence/3/user/')

    def test_get_residence_with_rooms(self):
        residence = models.Residence.objects.create(rfid='3')
        room1 = models.Room.objects.create(residence=residence)
        room2 = models.Room.objects.create(residence=residence)
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('rfid'), '3', 'RFID')
        self.assertEqual(response.data.get('url'), 'http://testserver/residence/3/')
        self.assertEqual(response.data.get('rooms_url'), 'http://testserver/residence/3/room/')
        self.assertEqual(response.data.get('users_url'), 'http://testserver/residence/3/user/')

    def test_get_residence_404(self):
        response = self.client.get('/residence/3/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_residence(self):
        response = self.client.post('/residence/', {'rfid': '3'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('rfid'), '3')

        residence = models.Residence.objects.get(rfid='3')
        self.assertEqual(residence.rfid, '3')

    def test_update_residence(self):
        residence = models.Residence.objects.create(rfid='3')

        response = self.client.put('/residence/3/', {'rfid': '42'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        residence = models.Residence.objects.get(rfid='42')
        self.assertEqual(residence.rfid, '42')

    def test_destroy_residence(self):
        residence = models.Residence.objects.create(rfid='3')
        self.assertEqual(residence.rfid, '3')

        response = self.client.delete('/residence/3/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        queryset = models.Residence.objects.filter(rfid='3')
        self.assertEqual(len(queryset), 0)


class ViewUserTestCase(APITestCase):

    residence = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')

    def test_list_users_empty(self):
        response = self.client.get('/residence/3/user/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_user_collection_contains_user_representations(self):
        user0 = models.User.objects.create(residence=self.residence, imei='123', name='Le Me')
        user1 = models.User.objects.create(residence=self.residence, imei='456', name='El user')

        response_user0 = self.client.get('/residence/3/user/123/')
        response_user1 = self.client.get('/residence/3/user/456/')
        response = self.client.get('/residence/3/user/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0], response_user0.data)
        self.assertEqual(response.data[1], response_user1.data)

    def test_user_representation_contains_imei_and_name(self):
        user0 = models.User.objects.create(residence=self.residence, imei='123', name='Le Me')

        response_user0 = self.client.get('/residence/3/user/123/')

        self.assertEqual(response_user0.status_code, status.HTTP_200_OK)
        self.assertEqual(response_user0.data.get('imei'), '123')
        self.assertEqual(response_user0.data.get('name'), 'Le Me')

    def test_get_non_existent_user_imei_results_in_404(self):
        response = self.client.get('/residence/3/user/123/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user(self):
        user_data = {'imei': '123', 'name': 'Le Me'}
        response = self.client.post('/residence/3/user/', user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = models.User.objects.get(imei='123')
        self.assertEqual(user.imei, '123')
        self.assertEqual(user.name, 'Le Me')


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
        self.assertEqual(response.data[0].get('residence').get('url'), 'http://testserver/residence/3/')

    def test_get_room(self):
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')

        response = self.client.get('/residence/3/room/%s/' % room.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), room.pk)
        self.assertEqual(response.data.get('url'), 'http://testserver/residence/3/room/%s/' % room.pk)
        self.assertEqual(response.data.get('name'), 'Dining Room')
        self.assertEqual(response.data.get('residence').get('url'), 'http://testserver/residence/3/')

    def test_get_room_404(self):
        response = self.client.get('/residence/3/room/1/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_room(self):
        response = self.client.post('/residence/3/room/', {'name': 'Dining Room'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_room(self):
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')

        response = self.client.put('/residence/3/room/%s/' % room.pk, {'name': 'Play Room'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        queryset = models.Room.objects.filter(pk=room.pk)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].pk, room.pk)
        self.assertEqual(queryset[0].name, 'Play Room')

    def test_destroy_room(self):
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')

        # Delete resource
        response = self.client.delete('/residence/3/room/%s/' % room.pk)

        # Test response code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Test room is deleted
        queryset = models.Room.objects.filter(pk=room.pk)
        self.assertEqual(len(queryset), 0)


class ViewThermostatTestCase(APITestCase):

    residence = None
    room = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')
        self.room = models.Room.objects.create(residence=self.residence, pk=1)

    def test_list_thermostats_empty(self):
        response = self.client.get('/residence/3/room/1/thermostat/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_single_thermostat(self):
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        response = self.client.get('/residence/3/room/1/thermostat/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('rfid'), '7e')
        self.assertEqual(response.data[0].get('room_pk'), 1)

    def test_get_thermostat(self):
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        response = self.client.get('/residence/3/room/1/thermostat/7e/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('rfid'), '7e')
        self.assertEqual(response.data.get('room_pk'), 1)
        self.assertEqual(response.data.get('temperatures_pk'), [])

    def test_get_thermostat_shows_temperatures(self):
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')
        temperature = models.Temperature.objects.create(thermostat=thermostat,
                                                        datetime='2015-04-30T12:00:00Z', value=36)

        response = self.client.get('/residence/3/room/1/thermostat/7e/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('rfid'), '7e')
        self.assertEqual(response.data.get('room_pk'), 1)
        self.assertEqual(len(response.data.get('temperatures_pk')), 1)
        self.assertEqual(str(response.data.get('temperatures_pk')[0]), '2015-04-30 12:00:00+00:00')

    def test_get_thermostat_404(self):
        response = self.client.get('/residence/3/room/1/thermostat/8/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_thermostat(self):
        data = {'rfid': '7e', 'room_pk': self.room.pk}
        response = self.client.post('/residence/3/room/1/thermostat/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('rfid'), '7e')

        queryset = models.Thermostat.objects.all().filter(rfid='7e')
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].rfid, '7e')

    def test_update_thermostat(self):
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        data = {'rfid': '42', 'room_pk': self.room.pk}
        response = self.client.put('/residence/3/room/1/thermostat/7e/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        queryset = models.Thermostat.objects.filter(rfid='42')
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].rfid, '42')
