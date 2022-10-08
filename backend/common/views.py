from rest_framework import mixins, viewsets
from shamrock import Shamrock
from .filtersets import DeviceFilter, SnapShotFilter
from .models import Device, Plant, Profile, SnapShot
from .serializers import DeviceSerializer, PlantSerializer, ShamrockSerializer, ProfileSerializer, SnapShotSerializer
from django.http import Http404


class SnapShotViewSet(viewsets.ModelViewSet):
    queryset = SnapShot.objects.all()
    serializer_class = SnapShotSerializer
    filterset_class = SnapShotFilter


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filterset_class = DeviceFilter


class PlantViewSet(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class ShamrockViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Not really a model, but an interface towards the Shamrock API.
    """
    serializer_class = ShamrockSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q")
        if not q:
            raise Http404
        shamrock = Shamrock(self.request.user.profile.remote_token, "https://api.floracodex.com/")
        objects = shamrock.search(q)["data"]
        return objects


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return super(ProfileViewSet, self).get_queryset().filter(user=self.request.user)
