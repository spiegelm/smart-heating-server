"""
Copyright 2016 Michael Spiegel, Wilhelm Kleiminger

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
