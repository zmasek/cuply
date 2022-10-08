from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.TextChoices):
    TEMPERATURE = "temperature", _("Temperature")
    HUMIDITY = "humidity", _("Humidity")
    LIGHT = "light", _("Light")


class FSMClass(models.TextChoices):
    ANALOG_SENSOR = "AnalogSensor", _("Analog Sensor")
    DIGITAL_ACTUATOR = "DigitalActuator", _("Digital Actuator")
    PWM = "PWM", _("PWM")
    I2C = "I2C", _("I2C")


class CurrentState(models.IntegerChoices):
    # https://en.wikipedia.org/wiki/BBCH-scale
    GERMINATING = 0, _("Germination, sprouting, bud development")
    LEAFING = 1, _("Leaf development")
    TILLERING = 2, _("Formation of side shoots, tillering")
    SHOOTING = 3, _("Stem elongation or rosette growth, shoot development")
    BOLTING = 4, _("Development of harvestable vegetative plant parts, bolting")
    HEADING = 5, _("Inflorescence emergence, heading")
    FLOWERING = 6, _("Flowering")
    FRUITING = 7, _("Development of fruit")
    RIPENING = 8, _("Ripening or maturity of fruit and seed")
    DORMANTING = 9, _("Senescence, beginning of dormancy")


ANALOG_SENSOR_BLOBS = [
    {"state": "very_low"},
    {"state": "low"},
    {"state": "medium"},
    {"state": "high"},
    {"state": "very_high"},
]
DIGITAL_ACTUATOR_BLOBS = [
    {"state": "off"},
    {"state": "on"},
]
I2C_BLOBS = [
    {"state": "very_low"},
    {"state": "low"},
    {"state": "medium"},
    {"state": "high"},
    {"state": "very_high"},
]
PWM_BLOBS = [
    {"state": "closed"},
    {"state": "opened"},
]
