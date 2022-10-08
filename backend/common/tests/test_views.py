import datetime
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework.test import APITestCase
from djangorestframework_camel_case.util import camelize
from .factories import SnapShotFactory, DeviceFactory, PlantFactory, UserFactory
from .utils import auth_user
from ..choices import FSMClass, Category, CurrentState
from ..models import SnapShot, Device, Plant, Profile
from ..views import SnapShotViewSet, DeviceViewSet, PlantViewSet, ShamrockViewSet, ProfileViewSet


class SnapShotViewSetTestCase(APITestCase):
    def setUp(self):
        user = UserFactory()
        self.snapshot = SnapShotFactory()
        self.device = DeviceFactory()
        self.url = reverse_lazy("snapshot-list")
        self.url_detail = reverse_lazy("snapshot-detail", kwargs={"pk": self.snapshot.pk})
        auth_user(self.client, user)

    def test_get_list(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["timestamp"], self.snapshot.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(result[0]["value"], self.snapshot.value)

    def test_get_list_filter_timestamp(self):
        response = self.client.get(self.url, data={"timestamp__date": timezone.now().strftime("%Y-%m-%d")}, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["timestamp"], self.snapshot.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(result[0]["value"], self.snapshot.value)

        response = self.client.get(self.url, data={"timestamp__date": (timezone.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")}, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result), 0)

    def test_get_list_filter_device_id(self):
        response = self.client.get(self.url, data={"device_id": self.snapshot.device.id}, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["timestamp"], self.snapshot.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(result[0]["value"], self.snapshot.value)

        response = self.client.get(self.url, data={"device_id": self.device.id}, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result), 0)

    def test_get_detail(self):
        response = self.client.get(self.url_detail, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["timestamp"], self.snapshot.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(result["value"], self.snapshot.value)

    def test_create(self):
        self.assertEqual(SnapShot.objects.count(), 1)
        data = {"value": 255, "device": self.device.id}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertTrue("timestamp" in result)
        self.assertEqual(result["value"], data["value"])
        self.assertNotEqual(self.device, self.snapshot.device)
        self.assertEqual(self.device.id, data["device"])
        self.assertEqual(result["device"], data["device"])
        self.assertEqual(SnapShot.objects.count(), 2)

    def test_put_update(self):
        value = self.snapshot.value
        device = self.snapshot.device.id
        data = {"value": 25, "device": self.device.id}
        response = self.client.put(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.snapshot.refresh_from_db()
        self.assertTrue("timestamp" in result)
        self.assertEqual(result["value"], data["value"])
        self.assertEqual(result["device"], data["device"])
        self.assertNotEqual(value, self.snapshot.value)
        self.assertNotEqual(device, self.snapshot.device.id)
        self.assertEqual(self.device, self.snapshot.device)

    def test_patch_update(self):
        value = self.snapshot.value
        device = self.snapshot.device.id
        data = {"value": 25}
        response = self.client.patch(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.snapshot.refresh_from_db()
        self.assertTrue("timestamp" in result)
        self.assertEqual(result["value"], data["value"])
        self.assertEqual(result["device"], self.snapshot.device.id)
        self.assertNotEqual(value, self.snapshot.value)
        self.assertEqual(device, self.snapshot.device.id)
        self.assertNotEqual(self.device, self.snapshot.device)

    def test_destroy(self):
        response = self.client.delete(self.url_detail, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(SnapShot.objects.exists())


class DeviceViewSetTestCase(APITestCase):
    def setUp(self):
        user = UserFactory()
        self.device = DeviceFactory()
        self.url = reverse_lazy("device-list")
        self.url_detail = reverse_lazy("device-detail", kwargs={"pk": self.device.pk})
        auth_user(self.client, user)

    def test_get_list(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["id"], self.device.id)
        self.assertEqual(result[0]["name"], self.device.name)
        self.assertEqual(result[0]["pin"], self.device.pin)
        self.assertEqual(result[0]["fsmClass"], self.device.fsm_class)
        self.assertEqual(result[0]["category"], self.device.category)
        self.assertEqual(result[0]["imageUrl"], "")
        self.assertEqual(result[0]["parent"], None)
        self.assertEqual(result[0]["thresholds"], camelize(self.device.thresholds))

    def test_get_list_filter_fsm_class(self):
        response = self.client.get(self.url, data={"fsm_class": "AnalogSensor"}, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["id"], self.device.id)
        self.assertEqual(result[0]["name"], self.device.name)
        self.assertEqual(result[0]["pin"], self.device.pin)
        self.assertEqual(result[0]["fsmClass"], self.device.fsm_class)
        self.assertEqual(result[0]["category"], self.device.category)
        self.assertEqual(result[0]["imageUrl"], "")
        self.assertEqual(result[0]["parent"], None)
        self.assertEqual(result[0]["thresholds"], camelize(self.device.thresholds))

        response = self.client.get(self.url, data={"fsm_class": "DigitalActuator"}, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result), 0)

    def test_get_detail(self):
        response = self.client.get(self.url_detail, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["id"], self.device.id)
        self.assertEqual(result["name"], self.device.name)
        self.assertEqual(result["pin"], self.device.pin)
        self.assertEqual(result["fsmClass"], self.device.fsm_class)
        self.assertEqual(result["category"], self.device.category)
        self.assertEqual(result["imageUrl"], "")
        self.assertEqual(result["parent"], None)
        self.assertEqual(result["thresholds"], camelize(self.device.thresholds))

    def test_create(self):
        self.assertEqual(Device.objects.count(), 1)
        data = {
            "name": "foo",
            "pin": "A4",
            "fsmClass": FSMClass.ANALOG_SENSOR,
            "category": Category.TEMPERATURE,
            "thresholds": {
                "veryLow": [0, 127],
                "low": [128, 255],
                "medium": [256, 767],
                "high": [768, 895],
                "veryHigh": [896, 1024],
            },
            "desiredState": "very_low",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertTrue("id" in result)
        self.assertEqual(result["name"], data["name"])
        self.assertEqual(result["pin"], data["pin"])
        self.assertEqual(result["fsmClass"], data["fsmClass"])
        self.assertEqual(result["category"], data["category"])
        self.assertEqual(result["imageUrl"], "")
        self.assertEqual(result["parent"], None)
        self.assertEqual(result["thresholds"], camelize(data["thresholds"]))
        self.assertEqual(Device.objects.count(), 2)

    def test_put_update(self):
        name = self.device.name
        pin = self.device.pin
        fsm_class = str(self.device.fsm_class)
        category = str(self.device.category)
        thresholds = self.device.thresholds
        data = {
            "name": "foo",
            "pin": "A4",
            "fsm_class": FSMClass.ANALOG_SENSOR,
            "category": Category.LIGHT,
            "thresholds": {
                "very_low": [0, 127],
                "low": [128, 255],
                "medium": [256, 767],
                "high": [768, 894],
                "very_high": [895, 1024],
            },
            "desiredState": "very_low",
        }
        response = self.client.put(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.device.refresh_from_db()
        self.assertTrue("id" in result)
        self.assertEqual(result["name"], data["name"])
        self.assertEqual(result["pin"], data["pin"])
        self.assertEqual(result["fsmClass"], data["fsm_class"])
        self.assertEqual(result["category"], data["category"])
        self.assertEqual(result["thresholds"], camelize(data["thresholds"]))
        self.assertEqual(result["imageUrl"], "")
        self.assertEqual(result["parent"], None)
        self.assertEqual(self.device.id, result["id"])
        self.assertNotEqual(name, self.device.name)
        self.assertNotEqual(pin, self.device.pin)
        self.assertEqual(fsm_class, self.device.fsm_class)
        self.assertNotEqual(category, self.device.category)
        self.assertNotEqual(thresholds, self.device.thresholds)

    def test_patch_update(self):
        name = self.device.name
        pin = self.device.pin
        fsm_class = str(self.device.fsm_class)
        category = str(self.device.category)
        thresholds = self.device.thresholds
        data = {
            "fsm_class": FSMClass.ANALOG_SENSOR,
            "category": Category.LIGHT,
            "thresholds": {
                "very_low": [0, 127],
                "low": [128, 255],
                "medium": [256, 767],
                "high": [768, 894],
                "very_high": [895, 1024],
            },
            "desiredState": "very_low",
        }
        response = self.client.patch(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.device.refresh_from_db()
        self.assertTrue("id" in result)
        self.assertEqual(result["name"], self.device.name)
        self.assertEqual(result["pin"], self.device.pin)
        self.assertEqual(result["fsmClass"], data["fsm_class"])
        self.assertEqual(result["category"], data["category"])
        self.assertEqual(result["thresholds"], camelize(data["thresholds"]))
        self.assertEqual(result["imageUrl"], "")
        self.assertEqual(result["parent"], None)
        self.assertEqual(self.device.id, result["id"])
        self.assertEqual(name, self.device.name)
        self.assertEqual(pin, self.device.pin)
        self.assertEqual(fsm_class, self.device.fsm_class)
        self.assertNotEqual(category, self.device.category)
        self.assertNotEqual(thresholds, self.device.thresholds)

    def test_destroy(self):
        response = self.client.delete(self.url_detail, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Device.objects.exists())


class PlantViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.plant = PlantFactory()
        self.url = reverse_lazy("plant-list")
        self.url_detail = reverse_lazy("plant-detail", kwargs={"pk": self.plant.pk})
        auth_user(self.client, self.user)

    def test_get_list(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["id"], self.plant.id)
        self.assertEqual(result[0]["remoteId"], str(self.plant.remote_id))
        self.assertEqual(result[0]["name"], self.plant.name)
        self.assertEqual(result[0]["imageUrl"], "")
        self.assertEqual(result[0]["timeInstalled"], self.plant.time_installed.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(result[0]["currentState"], self.plant.current_state)

    def test_get_detail(self):
        response = self.client.get(self.url_detail, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["id"], self.plant.id)
        self.assertEqual(result["remoteId"], str(self.plant.remote_id))
        self.assertEqual(result["name"], self.plant.name)
        self.assertEqual(result["imageUrl"], "")
        self.assertEqual(result["timeInstalled"], self.plant.time_installed.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEqual(result["currentState"], self.plant.current_state)

    @patch("common.serializers.Shamrock")
    def test_create(self, mock_Shamrock):
        self.assertEqual(Plant.objects.count(), 1)
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
        data = {
            "remoteId": "foo",
            "currentState": CurrentState.LEAFING,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertTrue("id" in result)
        self.assertEqual(result["remoteId"], data["remoteId"])
        self.assertEqual(result["currentState"], data["currentState"])
        self.assertEqual(result["name"], scientific_name)
        self.assertEqual(result["imageUrl"], image_url)
        self.assertTrue("timeInstalled" in result)
        mock_Shamrock.assert_called_once_with(self.user.profile.remote_token, "https://api.floracodex.com/")
        mock_shamrock.plants.assert_called_once_with(data["remoteId"])
        self.assertEqual(Plant.objects.count(), 2)

    @patch("common.serializers.Shamrock")
    def test_put_update(self, mock_Shamrock):
        remote_id = self.plant.remote_id
        current_state = self.plant.current_state
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
        data = {
            "remoteId": "foo_remote_id",
            "currentState": CurrentState.LEAFING,
        }
        response = self.client.put(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.plant.refresh_from_db()
        print(result)
        self.assertEqual(result["id"], self.plant.id)
        self.assertEqual(result["remoteId"], data["remoteId"])
        self.assertEqual(result["currentState"], data["currentState"])
        self.assertEqual(result["name"], scientific_name)
        self.assertEqual(result["imageUrl"], image_url)
        self.assertEqual(result["timeInstalled"], self.plant.time_installed.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        mock_Shamrock.assert_called_once_with(self.user.profile.remote_token, "https://api.floracodex.com/")
        mock_shamrock.plants.assert_called_once_with(data["remoteId"])

    @patch("common.serializers.Shamrock")
    def test_patch_update(self, mock_Shamrock):
        remote_id = self.plant.remote_id
        current_state = self.plant.current_state
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
        data = {
            "remoteId": "foo_remote_id",
        }
        response = self.client.patch(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.plant.refresh_from_db()
        print(result)
        self.assertEqual(result["id"], self.plant.id)
        self.assertEqual(result["remoteId"], data["remoteId"])
        self.assertEqual(result["currentState"], self.plant.current_state)
        self.assertEqual(result["name"], scientific_name)
        self.assertEqual(result["imageUrl"], image_url)
        self.assertEqual(result["timeInstalled"], self.plant.time_installed.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        mock_Shamrock.assert_called_once_with(self.user.profile.remote_token, "https://api.floracodex.com/")
        mock_shamrock.plants.assert_called_once_with(data["remoteId"])

    def test_destroy(self):
        response = self.client.delete(self.url_detail, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Plant.objects.exists())


class ShamrockViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url = reverse_lazy("shamrock-list")
        auth_user(self.client, self.user)

    def test_get_list_no_q(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 404)

    @patch("common.views.Shamrock")
    def test_get_list_q(self, mock_Shamrock):
        q = "foo plant"
        mock_shamrock = MagicMock()
        mock_Shamrock.return_value = mock_shamrock
        data = {
            "data": [
                {
                    "scientific_name": "foo",
                    "id": "foo_id",
                },
                {
                    "scientific_name": "bar",
                    "id": "bar_id",
                },
            ],
        }
        mock_shamrock.search.return_value = data
        response = self.client.get(self.url, data={"q": q}, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["id"], data["data"][0]["id"])
        self.assertEqual(result[0]["name"], data["data"][0]["scientific_name"])
        self.assertEqual(result[1]["id"], data["data"][1]["id"])
        self.assertEqual(result[1]["name"], data["data"][1]["scientific_name"])
        mock_Shamrock.assert_called_once_with(self.user.profile.remote_token, "https://api.floracodex.com/")
        mock_shamrock.search.assert_called_once_with(q)


class ProfileViewSetTestCase(APITestCase):
    def setUp(self):
        user = UserFactory()
        self.profile = user.profile
        self.url = reverse_lazy("profile-list")
        self.url_detail = reverse_lazy("profile-detail", kwargs={"pk": self.profile.pk})
        auth_user(self.client, user)

    def test_get_list(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result[0]["id"], self.profile.id)
        self.assertEqual(result[0]["remoteToken"], self.profile.remote_token)

    def test_get_detail(self):
        response = self.client.get(self.url_detail, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["id"], self.profile.id)
        self.assertEqual(result["remoteToken"], self.profile.remote_token)

    def test_create(self):
        self.assertEqual(Profile.objects.count(), 1)
        data = {"remote_token": "255"}
        # should not be able to create for the same user
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertEqual(result["detail"], "You already have a profile. Update it instead.")

        # should be able to create if a user doesn't have the profile
        user = UserFactory()
        user.profile.delete()
        self.assertEqual(Profile.objects.count(), 1)
        data = {"remote_token": "255"}
        auth_user(self.client, user)
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertTrue("id" in result)
        self.assertEqual(result["remoteToken"], data["remote_token"])
        self.assertEqual(Profile.objects.count(), 2)

    def test_put_update(self):
        remote_token = self.profile.remote_token
        data = {"remote_token": "25"}
        # should be able to update for the same user
        response = self.client.put(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.profile.refresh_from_db()
        self.assertTrue("id" in result)
        self.assertEqual(result["remoteToken"], data["remote_token"])
        self.assertNotEqual(remote_token, self.profile.remote_token)
        
        # should not be able to update for a different user
        data = {"remote_token": "25"}
        user = UserFactory()
        url_detail = reverse_lazy("profile-detail", kwargs={"pk": user.profile.pk})
        response = self.client.put(url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_patch_update(self):
        remote_token = self.profile.remote_token
        data = {"remote_token": "25"}
        # should be able to update for the same user
        response = self.client.patch(self.url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.profile.refresh_from_db()
        self.assertTrue("id" in result)
        self.assertEqual(result["remoteToken"], data["remote_token"])
        self.assertNotEqual(remote_token, self.profile.remote_token)
        
        # should not be able to update for a different user
        data = {"remote_token": "25"}
        user = UserFactory()
        url_detail = reverse_lazy("profile-detail", kwargs={"pk": user.profile.pk})
        response = self.client.patch(url_detail, data=data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_destroy(self):
        response = self.client.delete(self.url_detail, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Profile.objects.exists())
