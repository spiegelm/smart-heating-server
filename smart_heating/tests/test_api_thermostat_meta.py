from rest_framework import status, reverse
from rest_framework.test import APITestCase
from smart_heating import models

from django.utils import timezone
import datetime

class ViewThermostatMetaEntryTestCase(APITestCase):

    residence = None
    room = None
    thermostat = None

    def setUp(self):
        self.residence = models.Residence.objects.create(rfid='3')
        self.room = models.Room.objects.create(residence=self.residence, name='fancy room name')
        self.thermostat = models.Thermostat.objects.create(room=self.room, rfid='5')

    def test_meta_entries_collection_has_pagination(self):

        result = self.client.get('/residence/3/room/1/thermostat/5/meta_entry/')

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data.get('count'), 0)
        self.assertEqual(result.data.get('next_url'), None)
        self.assertEqual(result.data.get('previous_url'), None)
        self.assertEqual(result.data.get('latest_entry_url'),
                         'http://testserver/residence/3/room/1/thermostat/5/meta_entry/latest/')
        self.assertEqual(result.data.get('results'), [])

    def test_meta_entries_collection_consists_of_representations(self):
        date0 = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        date1 = datetime.datetime(2015, 5, 13, 8, 0, 0, 0, timezone.get_current_timezone())
        meta0 = models.ThermostatMetaEntry.objects.create(thermostat=self.thermostat, datetime=date0, rssi=-30, uptime=13, battery=3300)
        meta1 = models.ThermostatMetaEntry.objects.create(thermostat=self.thermostat, datetime=date1, rssi=-40, uptime=50, battery=3400)

        response_temp0 = self.client.get('/residence/3/room/1/thermostat/5/meta_entry/%s/' % meta0.pk)
        response_temp1 = self.client.get('/residence/3/room/1/thermostat/5/meta_entry/%s/' % meta1.pk)
        response = self.client.get('/residence/3/room/1/thermostat/5/meta_entry/')

        expected_results = [response_temp0.data, response_temp1.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(response.data.get('previous_url'), None)
        self.assertEqual(response.data.get('next_url'), None)
        self.assertEqual(response.data.get('results'), expected_results)

    def test_reverse_url(self):
        date0 = datetime.datetime(2015, 5, 13, 7, 0, 0, 0, timezone.get_current_timezone())
        meta0 = models.ThermostatMetaEntry.objects.create(thermostat=self.thermostat, datetime=date0, rssi=-30, uptime=13, battery=3300)

        url = reverse.reverse('thermostatmetaentry-detail', meta0.get_recursive_pks())
        self.assertEqual(url, '/residence/3/room/1/thermostat/5/meta_entry/%s/' % meta0.pk)

    # TODO def test_meta_representation_contains_rssi_uptime_battery(self):
