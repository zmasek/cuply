from django.db import IntegrityError, transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from shamrock import Shamrock, ShamrockException
from .choices import FSMClass, ANALOG_SENSOR_BLOBS, DIGITAL_ACTUATOR_BLOBS, I2C_BLOBS, PWM_BLOBS
from .models import Device, Plant, Profile, SnapShot, Microcontroller
from .utils import normalize_value
import logging

logger = logging.getLogger(__name__)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class DeviceSerializer(DynamicFieldsModelSerializer):
    image_url = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        return obj.image.url if obj.image else ""

    def get_parent(self, obj):
        if obj.parent is not None:
            return obj.parent.name

    class Meta:
        model = Device
        fields = ("id", "name", "pin", "fsm_class", "category", "image_url", "parent", "thresholds", "desired_state")

    def create(self, validated_data):
        if validated_data["fsm_class"] == FSMClass.ANALOG_SENSOR:
            validated_data["blob"] = ANALOG_SENSOR_BLOBS[2]
            if validated_data["blob"]["state"] not in validated_data["thresholds"]:
                raise serializers.ValidationError(_(f'The initial state "{validated_data["blob"]["state"]}" is not defined in thresholds ({validated_data["thresholds"]}).'))
        elif validated_data["fsm_class"] == FSMClass.DIGITAL_ACTUATOR:
            validated_data["blob"] = DIGITAL_ACTUATOR_BLOBS[0]
        elif validated_data["fsm_class"] == FSMClass.I2C:
            validated_data["blob"] = I2C_BLOBS[2]
            if validated_data["blob"]["state"] not in validated_data["thresholds"]:
                raise serializers.ValidationError(_(f'The initial state "{validated_data["blob"]["state"]}" is not defined in thresholds ({validated_data["thresholds"]}).'))
        elif validated_data["fsm_class"] == FSMClass.PWM:
            validated_data["blob"] = PWM_BLOBS[0]
        else:
            raise serializers.ValidationError(_(f"{validated_data['fsm_class']} devices cannot set the initial blob."))
        if validated_data["desired_state"] not in validated_data["thresholds"]:
            raise serializers.ValidationError(_(f'The desired state "{validated_data["desired_state"]}" is not found in the thresholds ({validated_data["thresholds"]}).'))
        validated_data["microcontroller_id"] = Microcontroller.objects.first().id
        return super().create(validated_data)


class SnapShotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnapShot
        fields = ('timestamp', "value", "device")


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ("id", "remote_id", "name", "image_url", "time_installed", "current_state")
        read_only_fields = ("name", "image_url",)

    def create(self, validated_data):
        remote_id = validated_data.get("remote_id")
        validated_data["name"], validated_data["image_url"] = self.get_shamrock_data(remote_id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        remote_id = validated_data.get('remote_id')
        if remote_id:
            instance.name, instance.image_url = self.get_shamrock_data(remote_id)
        return super().update(instance, validated_data)

    def get_shamrock_data(self, remote_id):
        """Invoke Shamrock to get the other data remotely and assign it to the instance."""
        shamrock = Shamrock(self.context["request"].user.profile.remote_token, "https://api.floracodex.com/")
        name = ""
        image_url = ""
        try:
            remote_data = shamrock.plants(remote_id)
        except ShamrockException as ex:
            message = "Couldn't connect to the remote service."
            logger.error(message)
            logger.error(repr(ex))
            raise serializers.ValidationError({"detail": message})
        try:
            name = remote_data["scientific_name"]
        except KeyError as ex:
            message = f"There is a response for {remote_id}, but it seems the API changed."
            logger.error(message)
            logger.error(repr(ex))
            raise serializers.ValidationError({"detail": message})
        image_url = remote_data.get("main_species", {}).get("image_url", "")
        return name, image_url


class ShamrockSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    common_name = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj["id"]

    def get_name(self, obj):
        return obj["scientific_name"]

    def get_image_url(self, obj):
        return obj.get("image_url")

    def get_common_name(self, obj):
        return obj.get("common_name")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "remote_token")

    @transaction.atomic
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        try:
            return super().create(validated_data)
        except IntegrityError as ex:
            message = "You already have a profile. Update it instead."
            logger.error(message)
            logger.error(repr(ex))
            raise serializers.ValidationError({"detail": message})
