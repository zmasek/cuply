from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers
from shamrock import ShamrockException
from ..choices import FSMClass, Category
from ..models import Plant, Device
from ..serializers import DeviceSerializer, SnapShotSerializer, PlantSerializer, ShamrockSerializer, ProfileSerializer
from .factories import DeviceFactory, SnapShotFactory, PlantFactory, UserFactory, MicrocontrollerFactory


class DeviceSerializerTestCase(TestCase):
    def setUp(self):
        self.microcontroller = MicrocontrollerFactory()
        self.device = DeviceFactory(microcontroller=self.microcontroller)

    def test_from_database(self):
        serializer = DeviceSerializer(self.device)
        self.assertEqual(serializer.data, {
            "id": self.device.id,
            "name": self.device.name,
            "pin": self.device.pin,
            "fsm_class": self.device.fsm_class,
            "category": self.device.category,
            "image_url": "",
            "parent": None,
            "thresholds": self.device.thresholds,
            "desired_state": self.device.desired_state,
        })

    def test_to_database(self):
        data = {
            "name": "foo",
            "pin": "A4",
            "fsm_class": FSMClass.ANALOG_SENSOR,
            "thresholds": {
                "very_low": [0, 127],
                "low": [128, 255],
                "medium": [256, 767],
                "high": [768, 895],
                "very_high": [896, 1024],
            },
            "desired_state": "very_low",
        }
        serializer = DeviceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data, data)

    def test_to_database_create_fail_blob_analog_sensor(self):
        self.assertEqual(Device.objects.count(), 1)
        data = {
            "name": "foo",
            "pin": "A4",
            "fsm_class": FSMClass.ANALOG_SENSOR,
            "category": Category.TEMPERATURE,
            "thresholds": {"foo": "bar"},
            "desired_state": "foo",
        }
        serializer = DeviceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.save()
        self.assertEqual(str(context.exception.detail[0]), f'The initial state "medium" is not defined in thresholds ({data["thresholds"]}).')
        self.assertEqual(Device.objects.count(), 1)

    def test_to_database_create_fail_blob_i2c(self):
        self.assertEqual(Device.objects.count(), 1)
        data = {
            "name": "foo",
            "pin": "A4",
            "fsm_class": FSMClass.I2C,
            "thresholds": {"foo": "bar"},
            "desired_state": "foo",
        }
        serializer = DeviceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.save()
        self.assertEqual(str(context.exception.detail[0]), f'The initial state "medium" is not defined in thresholds ({data["thresholds"]}).')
        self.assertEqual(Device.objects.count(), 1)

    def test_to_database_create_success(self):
        self.assertEqual(Device.objects.count(), 1)
        data = {
            "name": "foo",
            "pin": "A4",
            "fsm_class": FSMClass.ANALOG_SENSOR,
            "category": Category.TEMPERATURE,
            "thresholds": {
                "very_low": [0, 127],
                "low": [128, 255],
                "medium": [256, 767],
                "high": [768, 895],
                "very_high": [896, 1024],
            },
            "desired_state": "very_low",
        }
        serializer = DeviceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.assertEqual(Device.objects.count(), 2)
        new_device = Device.objects.last()
        self.assertEqual(new_device.name, data["name"])
        self.assertEqual(new_device.pin, data["pin"])
        self.assertEqual(new_device.microcontroller, self.microcontroller)


class SnapShotSerializerTestCase(TestCase):
    def setUp(self):
        self.device = DeviceFactory()
        self.snapshot = SnapShotFactory(device=self.device)

    def test_from_database(self):
        serializer = SnapShotSerializer(self.snapshot)
        self.assertEqual(serializer.data, {"timestamp": self.snapshot.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "value": self.snapshot.value, "device": self.snapshot.device.id})

    def test_to_database(self):
        data = {"value": 1, "device": self.device.id}
        serializer = SnapShotSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data, {"value": 1, "device": self.device})


class PlantSerializerTestCase(TestCase):
    def setUp(self):
        self.plant = PlantFactory()

    def test_from_database(self):
        serializer = PlantSerializer(self.plant)
        self.assertEqual(serializer.data, {
            "id": self.plant.id,
            "remote_id": str(self.plant.remote_id),
            "name": self.plant.name,
            "image_url": self.plant.image_url,
            "time_installed": self.plant.time_installed.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "current_state": self.plant.current_state,
        })

    def test_to_database(self):
        data = {
            "remote_id": "remote_foo",
            "current_state": 1,
        }
        serializer = PlantSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data, data)

    @patch("common.serializers.Shamrock")
    def test_to_database_create_shamrock_error(self, mock_Shamrock):
        data = {
            "remote_id": "remote_foo",
            "current_state": 1,
        }
        request = MagicMock()
        user = UserFactory()
        request.user.return_value = user
        serializer = PlantSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        mock_shamrock = MagicMock()
        mock_Shamrock.return_value = mock_shamrock
        scientific_name = "foo"
        image_url = "https://example.com/foo.jpeg"
        mock_shamrock.plants.side_effect = ShamrockException("Shamrock exception message")
        self.assertFalse(Plant.objects.exclude(id=self.plant.id).exists())
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.save()
        mock_Shamrock.assert_called_once_with(serializer.context["request"].user.profile.remote_token, "https://api.floracodex.com/")
        mock_shamrock.plants.assert_called_once_with(data["remote_id"])
        self.assertEqual(context.exception.detail["detail"], f"Couldn't connect to the remote service.")
        self.assertFalse(Plant.objects.exclude(id=self.plant.id).exists())


    @patch("common.serializers.Shamrock")
    def test_to_database_create_no_scientific_name(self, mock_Shamrock):
        data = {
            "remote_id": "remote_foo",
            "current_state": 1,
        }
        request = MagicMock()
        user = UserFactory()
        request.user.return_value = user
        serializer = PlantSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        mock_shamrock = MagicMock()
        mock_Shamrock.return_value = mock_shamrock
        scientific_name = "foo"
        image_url = "https://example.com/foo.jpeg"
        mock_shamrock.plants.return_value = {
            "scientific_name_changed": scientific_name,
            "main_species": {
                "image_url": image_url,
            },
        }
        self.assertFalse(Plant.objects.exclude(id=self.plant.id).exists())
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.save()
        mock_Shamrock.assert_called_once_with(serializer.context["request"].user.profile.remote_token, "https://api.floracodex.com/")
        mock_shamrock.plants.assert_called_once_with(data["remote_id"])
        self.assertEqual(context.exception.detail["detail"], f"There is a response for {data['remote_id']}, but it seems the API changed.")
        self.assertFalse(Plant.objects.exclude(id=self.plant.id).exists())

    @patch("common.serializers.Shamrock")
    def test_to_database_create_success(self, mock_Shamrock):
        data = {
            "remote_id": "remote_foo",
            "current_state": 1,
        }
        request = MagicMock()
        user = UserFactory()
        request.user.return_value = user
        serializer = PlantSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        mock_shamrock = MagicMock()
        mock_Shamrock.return_value = mock_shamrock
        scientific_name = "foo"
        image_url = "https://example.com/foo.jpeg"
        mock_shamrock.plants.return_value = {
            "scientific_name": scientific_name,
            "main_species": {
                "image_url": image_url,
            },
        }
        self.assertFalse(Plant.objects.exclude(id=self.plant.id).exists())
        serializer.save()
        mock_Shamrock.assert_called_once_with(serializer.context["request"].user.profile.remote_token, "https://api.floracodex.com/")
        mock_shamrock.plants.assert_called_once_with(data["remote_id"])
        self.assertEqual(Plant.objects.count(), 2)
        new_plant = Plant.objects.exclude(id=self.plant.id).first()
        self.assertEqual(new_plant.name, scientific_name)
        self.assertEqual(new_plant.image_url, image_url)


class ShamrockSerializerTestCase(TestCase):
    def setUp(self):
        self.shamrock = {"id": "foo", "scientific_name": "bar", "image_url": None, "common_name": None}

    def test_from_database(self):
        serializer = ShamrockSerializer(self.shamrock)
        self.assertEqual(serializer.data, {"id": "foo", "name": "bar", "image_url": None, "common_name": None})


class ProfileSerializerTestCase(TestCase):
    def setUp(self):
        user = UserFactory()
        self.profile = user.profile

    def test_from_database(self):
        serializer = ProfileSerializer(self.profile)
        self.assertEqual(serializer.data, {"id": self.profile.id, "remote_token": self.profile.remote_token})

    def test_to_database(self):
        data = {"remote_token": "foo"}
        serializer = ProfileSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data, data)
