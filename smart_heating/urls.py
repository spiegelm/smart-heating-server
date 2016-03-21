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

"""
Define the hierarchical mappings from URLs to views.
"""

from django.conf.urls import url, include
from rest_framework import routers

from smart_heating import views

router = routers.DefaultRouter()
router.register(r'residence', views.ResidenceViewSet)
router.register(r'residence/(?P<residence_pk>[^/.]+)/user', views.UserViewSet)
router.register(r'residence/(?P<residence_pk>[^/.]+)/room', views.RoomViewSet)
router.register(r'residence/(?P<residence_pk>[^/.]+)/room/(?P<room_pk>[^/.]+)/'
                r'thermostat', views.ThermostatViewSet)
router.register(r'residence/(?P<residence_pk>[^/.]+)/room/(?P<room_pk>[^/.]+)/'
                r'thermostat/(?P<thermostat_pk>[^/.]+)/temperature', views.TemperatureViewSet)
router.register(r'residence/(?P<residence_pk>[^/.]+)/room/(?P<room_pk>[^/.]+)/'
                r'thermostat/(?P<thermostat_pk>[^/.]+)/meta_entry', views.ThermostatMetaEntryViewSet)
router.register(r'residence/(?P<residence_pk>[^/.]+)/room/(?P<room_pk>[^/.]+)/'
                r'thermostat/(?P<thermostat_pk>[^/.]+)/heating_table', views.HeatingTableEntryViewSet)
router.register(r'device/raspberry', views.RaspberryDeviceViewSet)
router.register(r'device/thermostat', views.ThermostatDeviceViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
