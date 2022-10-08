import factory

from ..choices import Category
from ..models import default_blob


class MicrocontrollerFactory(factory.django.DjangoModelFactory):   
    name = factory.Faker('name')
    path="/dev/ttyACM0"

    class Meta:
        model = "common.Microcontroller"
        django_get_or_create = ("name", "path")
    


class DeviceFactory(factory.django.DjangoModelFactory):   
    name = factory.Faker("first_name")
    thresholds = {
        "very_low": [0, 127],
        "low": [128, 255],
        "medium": [256, 767],
        "high": [768, 895],
        "very_high": [896, 1024],
    }
    category = Category.TEMPERATURE
    microcontroller = factory.SubFactory(MicrocontrollerFactory)
    blob = default_blob()
    desired_state = "medium"

    class Meta:
        model = "common.Device"
        django_get_or_create = ("name", "thresholds", "category", "microcontroller", "blob", "desired_state")
    


class PlantFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    remote_id = factory.Faker('random_int')

    class Meta:
        model = "common.Plant"
        django_get_or_create = ("name", "remote_id")


class SnapShotFactory(factory.django.DjangoModelFactory):
    value = factory.Faker('random_int')
    device = factory.SubFactory(DeviceFactory)

    class Meta:
        model = "common.SnapShot"
        django_get_or_create = ("value", "device")
    

class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('name')
    last_name = factory.Faker('name')
    username = factory.Faker('name')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_staff = True
    is_superuser = True

    class Meta:
        model = "auth.User"
        django_get_or_create = ("first_name", "last_name", "username", "is_staff", "is_superuser")
