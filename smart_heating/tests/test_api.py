from rest_framework import status
from rest_framework.test import APITestCase
from smart_heating import models

from django.utils import timezone
import datetime


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

    def test_list_users_of_non_existent_residence(self):
        response = self.client.get('/residence/not-a-residence/user/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_get_user_of_unrelated_residence_404(self):
        unrelated_residence = models.Residence.objects.create(rfid='unrelated')
        user = models.User.objects.create(residence=self.residence, imei='123', name='Le Me')

        response = self.client.get('/residence/unrelated/user/123/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user(self):
        user_data = {'imei': '123', 'name': 'Le Me'}
        response = self.client.post('/residence/3/user/', user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = models.User.objects.get(imei='123')
        self.assertEqual(user.imei, '123')
        self.assertEqual(user.name, 'Le Me')

    # TODO test_update_user
    # TODO test_destroy_user


class ViewRoomTestCase(APITestCase):

    residence = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')

    def test_list_rooms_empty(self):
        response = self.client.get('/residence/3/room/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_rooms_of_non_existent_residence(self):
        response = self.client.get('/residence/not-a-residence/room/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_get_room_of_unrelated_residence_404(self):
        unrelated_residence = models.Residence.objects.create(rfid='unrelated')
        room = models.Room.objects.create(residence=self.residence, name='Dining Room')

        response = self.client.get('/residence/unrelated/room/%s/' % room.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_first_created_room_has_pk_1(self):
        response = self.client.post('/residence/3/room/', {'name': 'Dining Room'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        queryset = models.Room.objects.filter(pk=1)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].name, 'Dining Room')

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

    def test_list_thermostats_of_non_existent_residence(self):
        response = self.client.get('/residence/not-a-residence/room/1/thermostat/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_thermostats_of_non_existent_room(self):
        response = self.client.get('/residence/3/room/999/thermostat/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_single_thermostat(self):
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        response = self.client.get('/residence/3/room/1/thermostat/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('rfid'), '7e')
        self.assertEqual(response.data[0].get('room').get('url'), 'http://testserver/residence/3/room/1/')

    def test_get_thermostat(self):
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        response = self.client.get('/residence/3/room/1/thermostat/7e/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('rfid'), '7e')
        self.assertEqual(response.data.get('room').get('url'), 'http://testserver/residence/3/room/1/')
        self.assertEqual(response.data.get('temperatures_url'), 'http://testserver/residence/3/room/1/'
                                                                'thermostat/7e/temperature/')

    def test_get_thermostat_404(self):
        response = self.client.get('/residence/3/room/1/thermostat/8/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_thermostat_of_unrelated_residence_404(self):
        unrelated_residence = models.Residence.objects.create(rfid='unrelated')
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        response = self.client.get('/residence/unrelated/room/1/thermostat/7e/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_thermostat_of_unrelated_room_404(self):
        unrelated_room = models.Room.objects.create(residence=self.residence, name='Unrelated Room')
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        response = self.client.get('/residence/unrelated/room/%s/thermostat/7e/' % unrelated_room.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_thermostat(self):
        data = {'rfid': '7e'}
        response = self.client.post('/residence/3/room/1/thermostat/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('rfid'), '7e')

        queryset = models.Thermostat.objects.all().filter(rfid='7e')
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].rfid, '7e')

    def test_update_thermostat(self):
        thermostat = models.Thermostat.objects.create(room=self.room, rfid='7e')

        data = {'rfid': '42'}
        response = self.client.put('/residence/3/room/1/thermostat/7e/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        queryset = models.Thermostat.objects.filter(rfid='42')
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].rfid, '42')

    # TODO test_destroy_thermostat


class ViewTemperatureTestCase(APITestCase):

    residence = None
    room = None
    thermostat = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')
        self.room = models.Room.objects.create(residence=self.residence, name='fancy room name')
        self.thermostat = models.Thermostat.objects.create(room=self.room, rfid='5')

    def test_list_temperatures_empty_with_pagination(self):
        result = self.client.get('/residence/3/room/1/thermostat/5/temperature/')

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data.get('count'), 0)
        self.assertEqual(result.data.get('next_url'), None)
        self.assertEqual(result.data.get('previous_url'), None)
        self.assertEqual(result.data.get('latest_temperature_url'), 'http://testserver/residence/3/room/1/thermostat/5/temperature/latest/')
        self.assertEqual(result.data.get('chart_url'), 'http://testserver/residence/3/room/1/thermostat/5/temperature/chart/')
        self.assertEqual(result.data.get('results'), [])

    def test_list_temperatures_of_non_existent_residence(self):
        response = self.client.get('/residence/not-a-residence/room/1/thermostat/5/temperature/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_temperatures_of_non_existent_room(self):
        response = self.client.get('/residence/3/room/999/thermostat/5/temperature/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_temperatures_of_non_existent_thermostat(self):
        response = self.client.get('/residence/3/room/1/thermostat/999/temperature/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_temperatures_of_unrelated_residence_404(self):
        unrelated_residence = models.Residence.objects.create(rfid='UNRELATED')

        self.assertEqual(self.client.get('/residence/3/room/1/thermostat/5/temperature/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/residence/UNRELATED/room/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/residence/UNRELATED/room/1/thermostat/5/temperature/').status_code, status.HTTP_404_NOT_FOUND)

    def test_list_temperatures_of_unrelated_room_404(self):
        unrelated_room = models.Room.objects.create(residence=self.residence, name='Unrelated Room')

        response = self.client.get('/residence/3/room/%s/thermostat/5/temperature/' % unrelated_room.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_temperature_collection_contains_temperature_representations(self):
        """
        Temperature collection contains temperature representations ordered by datetime
        """
        date0 = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        date1 = datetime.datetime(2015, 5, 13, 8, 0, 0, 0, timezone.get_current_timezone())
        temperature0 = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date0, value=36.1)
        temperature1 = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date1, value=36.4)

        response_temp0 = self.client.get('/residence/3/room/1/thermostat/5/temperature/%s/' % date0.isoformat())
        response_temp1 = self.client.get('/residence/3/room/1/thermostat/5/temperature/%s/' % date1.isoformat())
        response = self.client.get('/residence/3/room/1/thermostat/5/temperature/')

        expected_results = [response_temp0.data, response_temp1.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(response.data.get('next_url'), None)
        self.assertEqual(response.data.get('results'), expected_results)

    def test_get_temperature_representation_contains_datetime_and_value(self):
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date, value=36.1)

        response = self.client.get('/residence/3/room/1/thermostat/5/temperature/%s/' % date.isoformat())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('url'),
                         'http://testserver/residence/3/room/1/thermostat/5/temperature/%s/' % date.isoformat())
        self.assertEqual(response.data.get('thermostat').get('url'),
                         'http://testserver/residence/3/room/1/thermostat/5/')
        self.assertEqual(response.data.get('datetime'), '2015-05-13T07:00:00Z')
        self.assertEqual(response.data.get('value'), 36.1)

    def test_get_temperature_404(self):
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())

        response = self.client.get('/residence/3/room/1/thermostat/5/temperature/%s/' % date.isoformat())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_temperature_of_unrelated_thermostat_404(self):
        unrelated_thermostat = models.Thermostat.objects.create(room=self.room, rfid='UNRELATED')
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date, value=36.1)

        self.assertEqual(self.client.get('/residence/3/room/1/thermostat/5/temperature/')
                         .status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/residence/3/room/1/thermostat/UNRELATED/temperature/')
                         .status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/residence/3/room/1/thermostat/UNRELATED/temperature/%s/' % date.isoformat())
                         .status_code, status.HTTP_404_NOT_FOUND)

    def test_create_temperature(self):
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature_data = {'datetime': date.isoformat(), 'value': 25.3}
        response = self.client.post('/residence/3/room/1/thermostat/5/temperature/', temperature_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check stored values
        temperature = models.Temperature.objects.get(datetime=date.isoformat())
        self.assertEqual(temperature.datetime.isoformat(), date.isoformat())
        self.assertEqual(temperature.value, 25.3)
        self.assertEqual(temperature.thermostat, self.thermostat)

    def test_create_temperature_allow_valid_value_range(self):
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature_data = {'datetime': date.isoformat(), 'value': 5}
        response = self.client.post('/residence/3/room/1/thermostat/5/temperature/', temperature_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        date = datetime.datetime(2015, 5, 13, 8, 0, 0, 0, timezone.get_current_timezone())
        temperature_data = {'datetime': date.isoformat(), 'value': 30}
        response = self.client.post('/residence/3/room/1/thermostat/5/temperature/', temperature_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_temperature_deny_invalid_value_range(self):
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature_data = {'datetime': date.isoformat(), 'value': 4}
        response = self.client.post('/residence/3/room/1/thermostat/5/temperature/', temperature_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature_data = {'datetime': date.isoformat(), 'value': 31}
        response = self.client.post('/residence/3/room/1/thermostat/5/temperature/', temperature_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_temperature(self):
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date, value=36.1)

        new_date = date + datetime.timedelta(days=1)
        data = {'datetime': new_date, 'value': 22.5}
        response = self.client.put('/residence/3/room/1/thermostat/5/temperature/%s/' % date.isoformat(), data)

        # Check stored values
        temperature = models.Temperature.objects.get(datetime=new_date.isoformat())
        self.assertEqual(temperature.datetime.isoformat(), '2015-05-14T07:00:00+00:00')
        self.assertEqual(temperature.value, 22.5)
        self.assertEqual(temperature.thermostat, self.thermostat)

    def test_destroy_temperature(self):
        date = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date, value=36.1)

        queryset = models.Temperature.objects.filter(datetime=date)
        self.assertEqual(len(queryset), 1)

        response = self.client.delete('/residence/3/room/1/thermostat/5/temperature/%s/' % date.isoformat())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        queryset = models.Temperature.objects.filter(datetime=date)
        self.assertEqual(len(queryset), 0)

    def test_get_latest_temperature(self):
        date0 = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        date1 = datetime.datetime(2015, 5, 14, 7, 0, 0, 0, timezone.get_current_timezone())
        temperature0 = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date0, value=36.1)
        temperature1 = models.Temperature.objects.create(thermostat=self.thermostat, datetime=date1, value=36.1)

        response = self.client.get('/residence/3/room/1/thermostat/5/temperature/latest/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('datetime'), '2015-05-14T07:00:00Z')

    def test_get_latest_temperature_without_temperatures_results_in_404(self):
        response = self.client.get('/residence/3/room/1/thermostat/5/temperature/latest/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ViewHeatingTableTestCase(APITestCase):

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')
        self.room = models.Room.objects.create(residence=self.residence, name='fancy room name')
        self.thermostat = models.Thermostat.objects.create(room=self.room, rfid='5')

    def test_heating_table_entry_representation(self):

        time = datetime.datetime(2000, 1, 1, 13, 45, 0).time()
        entry = models.HeatingTableEntry.objects.create(thermostat=self.thermostat,
                                                        day=models.HeatingTableEntry.MONDAY, time=time, temperature=23.0)

        response = self.client.get('/residence/3/room/1/thermostat/5/heating_table/%s/' % entry.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('day'), models.HeatingTableEntry.MONDAY)
        self.assertEqual(response.data.get('time'), '13:45:00')

    def test_create_heating_table_entry(self):

        data = {'day': models.HeatingTableEntry.MONDAY, 'time': '13:45:00', 'temperature': 25.67}
        response = self.client.post('/residence/3/room/1/thermostat/5/heating_table/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_heating_table_entry_duplicate(self):

        data = {'day': models.HeatingTableEntry.MONDAY, 'time': '13:45:00', 'temperature': 25.67}
        response = self.client.post('/residence/3/room/1/thermostat/5/heating_table/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'day': models.HeatingTableEntry.MONDAY, 'time': '13:45:00', 'temperature': 25.67}
        response = self.client.post('/residence/3/room/1/thermostat/5/heating_table/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('non_field_errors'), ['The fields day, time, thermostat must make a unique set.'])

    def test_create_heating_table_entry_duplicate_date_time_in_separate_thermostat(self):

        second_thermostat = models.Thermostat.objects.create(room=self.room, rfid='5b')

        data = {'day': models.HeatingTableEntry.MONDAY, 'time': '13:45:00', 'temperature': 25.67}
        response = self.client.post('/residence/3/room/1/thermostat/5/heating_table/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'day': models.HeatingTableEntry.MONDAY, 'time': '13:45:00', 'temperature': 25.67}
        response = self.client.post('/residence/3/room/1/thermostat/%s/heating_table/' % second_thermostat.pk, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_heating_table_entry(self):

        time = datetime.datetime(2000, 1, 1, 13, 45, 0).time()
        entry = models.HeatingTableEntry.objects.create(thermostat=self.thermostat,
                                                        day=models.HeatingTableEntry.MONDAY, time=time, temperature=23.0)

        data = {'day': models.HeatingTableEntry.MONDAY, 'time': '13:45:00', 'temperature': 25.67}
        response = self.client.put('/residence/3/room/1/thermostat/5/heating_table/%s/' % entry.pk, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_heating_table_entries_ordered_by_date_and_time(self):
        time12 = datetime.datetime(2000, 1, 1, 12, 0, 0).time()
        time13 = datetime.datetime(2000, 1, 1, 13, 0, 0).time()
        entry_tue_13 = models.HeatingTableEntry.objects.create(
            thermostat=self.thermostat, day=models.HeatingTableEntry.TUESDAY, time=time13, temperature=23.0)
        entry_tue_12 = models.HeatingTableEntry.objects.create(
            thermostat=self.thermostat, day=models.HeatingTableEntry.TUESDAY, time=time12, temperature=23.0)
        entry_mon_12 = models.HeatingTableEntry.objects.create(
            thermostat=self.thermostat, day=models.HeatingTableEntry.MONDAY, time=time12, temperature=23.0)
        entry_fri_13 = models.HeatingTableEntry.objects.create(
            thermostat=self.thermostat, day=models.HeatingTableEntry.FRIDAY, time=time13,temperature=23.0)
        entry_mon_13 = models.HeatingTableEntry.objects.create(
            thermostat=self.thermostat, day=models.HeatingTableEntry.MONDAY, time=time13, temperature=23.0)

        response = self.client.get('/residence/3/room/1/thermostat/5/heating_table/')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data[0].get('id'), entry_mon_12.id)
        self.assertEqual(response.data[1].get('id'), entry_mon_13.id)
        self.assertEqual(response.data[2].get('id'), entry_tue_12.id)
        self.assertEqual(response.data[3].get('id'), entry_tue_13.id)
        self.assertEqual(response.data[4].get('id'), entry_fri_13.id)


class ViewRaspberryDeviceTestCase(APITestCase):
    # TODO test raspberry device
    pass


class ViewThermostatDeviceTestCase(APITestCase):
    # TODO test thermostat device
    pass
