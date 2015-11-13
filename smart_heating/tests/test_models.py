from django.test import TestCase
from smart_heating.models import *


class ResidenceTestCase(TestCase):
    def setUp(self):
        pass

    def test_residence_can_be_created(self):
        """Residence model can be created"""
        residence = Residence.objects.create(rfid='3')

    def test_residence_can_be_created_and_retrieved(self):
        """Residence model can be created and retrieved"""
        residence = Residence.objects.create(rfid='3')
        residence = Residence.objects.get(rfid='3')
        self.assertEqual(residence.rfid, '3')
