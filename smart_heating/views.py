from django.http.response import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, renderers, mixins
from rest_framework.decorators import list_route

from smart_heating.pagination import *
from smart_heating.serializers import *


class HierarchicalModelHelper:
    def get_room(self):
        residence_pk = self.kwargs.get('residence_pk')
        room_pk = self.kwargs.get('room_pk')
        return get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)

    def get_thermostat(self):
        room_pk = self.kwargs.get('room_pk')
        thermostat_pk = self.kwargs.get('thermostat_pk')
        return get_object_or_404(Thermostat.objects.all(), room=room_pk, pk=thermostat_pk)

    @abstractmethod
    def get_parent(self):
        """
        Returns a dictionary of {parent_name: parent_model_instance}.
        """
        pass

    @abstractmethod
    def check_hierarchy(self):
        """
        Checks if the URL arguments match the parents of the queried model.
        """
        pass

    def get_queryset(self):
        self.check_hierarchy()
        return self.queryset.filter(**self.get_parent())

    def get_serializer_extra_data(self):
        return self.get_parent()



class ProtectedModelViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet,
                            HierarchicalModelHelper):
    """
    A viewset that provides default `create()`, `retrieve()`,
    `destroy()` and `list()` actions.
    """
    pass


class HierarchicalModelViewSet(HierarchicalModelHelper,
                               viewsets.ModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        context['extra_data'] = self.get_serializer_extra_data()
        return context


class ResidenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows residences to be viewed or edited.
    """
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer


class UserViewSet(HierarchicalModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_residence(self):
        return get_object_or_404(Residence.objects.all(), pk=self.kwargs['residence_pk'])

    def get_parent(self):
        return {'residence': self.get_residence()}


class RoomViewSet(viewsets.ModelViewSet):

    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_queryset(self):
        residence_pk = self.kwargs.get('residence_pk')
        get_object_or_404(Residence.objects.all(), pk=residence_pk)
        return Room.objects.filter(residence=residence_pk)

    def perform_create(self, serializer):
        # Grab residence from kwargs provided by the router
        residence = Residence.objects.get(pk=self.kwargs.get('residence_pk'))
        # Add residence information to the serializer
        serializer.save(residence=residence)


class ThermostatViewSet(viewsets.ModelViewSet):

    queryset = Thermostat.objects.all()
    serializer_class = ThermostatSerializer

    def get_queryset(self):
        residence_pk = self.kwargs.get('residence_pk')
        room_pk = self.kwargs.get('room_pk')
        get_object_or_404(Room.objects.all(), residence=residence_pk, pk=room_pk)
        return Thermostat.objects.filter(room=room_pk)

    def perform_create(self, serializer):
        # Grab room from kwargs provided by the router
        room = Room.objects.get(pk=self.kwargs.get('room_pk'))
        # Add residence information to the serializer
        serializer.save(room=room)


class TemperatureViewSet(HierarchicalModelViewSet):

    queryset = Temperature.objects.all()
    serializer_class = TemperatureSerializer

    # Allow dots in the lookup value as the datetime primary key uses a dot to represent milliseconds
    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        # check residence, room and thermostat in hierarchy
        self.get_room()
        self.get_thermostat()
        thermostat_pk = self.kwargs.get('thermostat_pk')
        return Temperature.objects.filter(thermostat=thermostat_pk)

    def perform_create(self, serializer):
        # Grab thermostat from kwargs provided by the router
        thermostat = Thermostat.objects.get(pk=self.kwargs.get('thermostat_pk'))
        # Add parent information to the serializer
        serializer.save(thermostat=thermostat)

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request, *args, **kwargs):
        temperatures = self.get_queryset().order_by('-datetime')
        if len(temperatures) == 0:
            raise Http404('There are no temperatures.')
        latest_temperature = temperatures[0]
        return Response(self.get_serializer(latest_temperature).data)

    @list_route(methods=['get'], url_path='chart', renderer_classes=[renderers.TemplateHTMLRenderer])
    def chart(self, request, *args, **kwargs):
        temperatures = self.get_queryset()
        print(temperatures)
        context = {
            'temperatures': [[int(t.datetime.timestamp()*1000), t.value] for t in temperatures],
            'room': self.get_room(),
            'thermostat': self.get_thermostat()
        }
        return render(request, 'smart_heating/temperature_chart.html', context)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        # Override the paginator property to inject the kwargs to the paginator. This is required
        # to generate the latest_temperature_url.
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = TemperaturePagination(kwargs=self.kwargs)
        return self._paginator

class ThermostatMetaEntryViewSet(ProtectedModelViewSet):

    queryset = ThermostatMetaEntry.objects.all()
    serializer_class = ThermostatMetaEntrySerializer

    def get_queryset(self):
        # check residence, room and thermostat in hierarchy
        self.get_room()
        self.get_thermostat()
        thermostat_pk = self.kwargs.get('thermostat_pk')
        return ThermostatMetaEntry.objects.filter(thermostat=thermostat_pk)

    def perform_create(self, serializer):
        # Grab thermostat from kwargs provided by the router
        thermostat = Thermostat.objects.get(pk=self.kwargs.get('thermostat_pk'))
        # Add parent information to the serializer
        serializer.save(thermostat=thermostat)

    @list_route(methods=['get'], url_path='latest')
    def latest(self, request, *args, **kwargs):
        meta_entries = self.get_queryset().order_by('-datetime')
        if len(meta_entries) == 0:
            raise Http404('There are no meta entries.')
        latest_temperature = meta_entries[0]
        return Response(self.get_serializer(latest_temperature).data)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        # Override the paginator property to inject the kwargs to the paginator. This is required
        # to generate the url for the latest entry.
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                # TODO rename Pagination
                self._paginator = ThermostatMetaEntriesPagination(kwargs=self.kwargs)
        return self._paginator


class HeatingTableEntryViewSet(HierarchicalModelViewSet):

    queryset = HeatingTableEntry.objects.all()
    serializer_class = HeatingTableEntrySerializer

    def get_parent(self):
        return {'thermostat': self.get_thermostat()}

    def check_hierarchy(self):
        # Check residence, room and thermostat in hierarchy
        self.get_room()         # This includes the residence check
        self.get_thermostat()


class DeviceLookupMixin(viewsets.ModelViewSet):

    @list_route(methods=['get'], url_path='lookup')
    def lookup(self, request, *args, **kwargs):
        mac = request.GET.get('mac')
        if mac is None:
            return Response(status=400, data={'mac': ['This field is required']})
        device = get_object_or_404(self.get_queryset(), mac=mac)
        serializer = self.get_serializer(device)
        return Response(serializer.data)


class RaspberryDeviceViewSet(DeviceLookupMixin,
                             viewsets.ModelViewSet):

    queryset = RaspberryDevice.objects.all()
    serializer_class = RaspberryDeviceSerializer


class ThermostatDeviceViewSet(DeviceLookupMixin,
                              viewsets.ModelViewSet):

    queryset = ThermostatDevice.objects.all()
    serializer_class = ThermostatDeviceSerializer
