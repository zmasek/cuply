from django.test import TestCase
from .factories import DeviceFactory, UserFactory
from ..loop_manager import q


class PostSaveUpdateDevicesTestCase(TestCase):
    def setUp(self):
        q.queue.clear()

    def test_device_created(self):
        self.assertTrue(q.empty())
        device = DeviceFactory()
        self.assertFalse(q.empty())
        result = q.get()
        self.assertEqual(result, {"created": device.id})

    def test_device_updated(self):
        device = DeviceFactory()
        q.queue.clear()
        device.name = "foo"
        device.save()
        self.assertFalse(q.empty())
        result = q.get()
        self.assertEqual(result, {"updated": device.id})


class PostDeleteUpdateDevicesTestCase(TestCase):
    def setUp(self):
        self.device = DeviceFactory()
        q.queue.clear()
    
    def test_device_deleted(self):
        self.assertTrue(q.empty())
        device_id = self.device.id
        self.device.delete()
        self.assertFalse(q.empty())
        result = q.get()
        self.assertEqual(result, {"deleted": device_id})


class PostSaveCreateProfileTestCase(TestCase):
    def test_profile_created(self):
        user = UserFactory()
        self.assertIsNotNone(user.profile)
