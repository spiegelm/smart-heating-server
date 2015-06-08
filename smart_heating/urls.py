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

