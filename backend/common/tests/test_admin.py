from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

# SnapShotAdmin, PlantAdmin, MicrocontrollerAdmin are not using anything special
from ..admin import DeviceAdmin, CustomUserAdmin
from ..models import Device

from .factories import UserFactory


class DeviceAdminTestCase(TestCase):
    def setUp(self):
        self.device_admin = DeviceAdmin(Device, AdminSite())

    def test_is_mptt_admin(self):
        bases = [base.__name__ for base in self.device_admin.__class__.__bases__]
        self.assertTrue("DraggableMPTTAdmin" in bases)


class UserAdminTestCase(TestCase):
    def setUp(self):
        self.remote_token = "foo"
        self.user = UserFactory()
        self.user_admin = CustomUserAdmin(User, AdminSite())
    
    def test_get_token(self):
        self.user.profile.remote_token = self.remote_token
        self.user.profile.save()
        self.assertEqual(self.user_admin.get_token(self.user), self.remote_token)

    def test_get_inline_instances_empty(self):
        request = RequestFactory()
        self.user.profile.delete()
        request.user = self.user
        inline_instances = self.user_admin.get_inline_instances(request, obj=self.user)
        self.assertEqual(len(inline_instances[0].get_queryset(request)), 0)

    def test_get_inline_instances(self):
        request = RequestFactory()
        request.user = self.user
        profile = self.user.profile
        profile.remote_token = self.remote_token
        profile.save()
        inline_instances = self.user_admin.get_inline_instances(request, obj=self.user)
        self.assertEqual(inline_instances[0].get_queryset(request)[0], profile)
