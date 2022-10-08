import rest_framework_filters as filtersets

from .models import Device, SnapShot


class SnapShotFilter(filtersets.FilterSet):
    timestamp__date = filtersets.DateFilter(field_name="timestamp", lookup_expr='date')

    class Meta:
        model = SnapShot
        fields = ['device_id', 'timestamp__date']


class DeviceFilter(filtersets.FilterSet):
    class Meta:
        model = Device
        fields = ['fsm_class']
