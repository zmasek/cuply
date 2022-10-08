import json
import keyword
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .mixins import DeviceMixin, MicrocontrollerMixin
from .choices import Category, FSMClass, CurrentState, ANALOG_SENSOR_BLOBS, DIGITAL_ACTUATOR_BLOBS, PWM_BLOBS, I2C_BLOBS
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
# the following are imported in the global namespace, and used later dynamically so it's not a direct call
# this is done in get_fsm method of Device class
from .fsm import DigitalActuator, AnalogSensor, I2C, PWM


class Microcontroller(models.Model, MicrocontrollerMixin):
    name = models.CharField(_("name"), max_length=50)
    description = models.TextField(_("description"), blank=True, default="")
    path = models.CharField(_("path"), max_length=255)  # /dev/ttyACM0

    class Meta:
        verbose_name = _("Microcontroller")
        verbose_name_plural = _("Microcontrollers")
        ordering = ("name",)

    def __str__(self):
        return self.name


def default_blob():
    return {"state": "medium"}


def validate_attr_compatible(value):
    if not (value.isidentifier() and not keyword.iskeyword(value)):
        raise ValidationError(
            _(f"{value} is not attr compatible."),
        )


class Device(MPTTModel, DeviceMixin):
    fsm_class = models.CharField(_('FSM class'), max_length=50, choices=FSMClass.choices, default=FSMClass.ANALOG_SENSOR)
    category = models.CharField(_("category"), max_length=50, blank=True, default="", choices=Category.choices)
    name = models.CharField(_("name"), max_length=50, unique=True, validators=[validate_attr_compatible])  # temperature
    description = models.TextField(_("description"), blank=True, default="")
    pin = models.CharField(_("pin"), max_length=50, blank=True, default="")  # A0
    blob = models.JSONField(_(u"blob"), max_length=50, default=default_blob)  # the state the device is in reported from the FSM
    unit = models.CharField(_("unit"), max_length=50, blank=True, default="")  # like celsius or lumens, but this is usually not necessary
    microcontroller = models.ForeignKey(Microcontroller, on_delete=models.CASCADE, verbose_name=_("microcontroller"))
    image = models.ImageField(blank=True, null=True, max_length=255, upload_to="devices")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    # after and before fields are for the time-lock, i.e. they are used to check things happening for example after 7 in the morning and before 19 in the afternoon
    # although I'm not sure how night works, after 19 and before 7?
    after = models.TimeField(_("after"), default=timezone.datetime.time(timezone.datetime(2021, 1, 1, 8, 0, 0)), null=True, blank=True)
    before = models.TimeField(_("before"), default=timezone.datetime.time(timezone.datetime(2021, 1, 1, 21, 0, 0)), null=True, blank=True)
    # thresholds = {"high": [13, 23], ...} this is used to check the state against the thresholds when it should transition
    thresholds = models.JSONField(_("thresholds"), default=dict)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    desired_state = models.CharField(_("desired state"), max_length=50, default="")

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = ("-created",)

    def __str__(self):
        return self.name

    def get_fsm(self, microcontroller):
        """
            Return the instance of globally imported FSM class dynamically for this device. Run only once as a singleton?
        """
        return globals()[self.fsm_class].from_blob(self.blob, microcontroller, self, self.get_children())

    def get_kind(self):
        if self.fsm_class in {
            FSMClass.ANALOG_SENSOR,
            FSMClass.I2C,
        }:
            return "sensor"
        return "actuator"

    def clean(self):
        if self.fsm_class == FSMClass.ANALOG_SENSOR and not self.category:
            raise ValidationError(_('AnalogSensor devices must have category set.'))
        if self.fsm_class == FSMClass.ANALOG_SENSOR:
            if not self.blob in ANALOG_SENSOR_BLOBS:
                raise ValidationError(_(f'AnalogSensor devices can have blobs from {ANALOG_SENSOR_BLOBS}.'))
            if self.blob["state"] not in self.thresholds:
                raise ValidationError(_(f'The state "{self.blob["state"]}" is not defined in thresholds ({self.thresholds}).'))
        if self.fsm_class == FSMClass.DIGITAL_ACTUATOR:
            if not self.blob in DIGITAL_ACTUATOR_BLOBS:
                raise ValidationError(_(f'DigitalActuator devices can have blobs from {DIGITAL_ACTUATOR_BLOBS}.'))
        if self.fsm_class == FSMClass.I2C:
            if not self.blob in I2C_BLOBS:
                raise ValidationError(_(f'I2C devices can have blobs from {I2C_BLOBS}.'))
            if self.blob["state"] not in self.thresholds:
                raise ValidationError(_(f'The state "{self.blob["state"]}" is not defined in thresholds ({self.thresholds}).'))
        if self.fsm_class == FSMClass.PWM:
            if not self.blob in PWM_BLOBS:
                raise ValidationError(_(f'PWM devices can have blobs from {PWM_BLOBS}.'))
        if self.desired_state not in self.thresholds:
            raise ValidationError(_(f'The desired state "{self.desired_state}" is not defined in thresholds ({self.thresholds}).'))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Plant(models.Model):
    time_installed = models.DateTimeField(auto_now_add=True)
    current_state = models.IntegerField(_("current state"), default=CurrentState.BOLTING, choices=CurrentState.choices)
    # thresholds would be nice here from api

    remote_id = models.CharField(max_length=24)

    name = models.CharField(blank=True, max_length=255)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


# TODO: Profile should also house the fields for telegram
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    remote_token = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user",)
        get_latest_by = "user.created"

    def __str__(self):
        return f"Profile - {self.user.get_full_name()}"


class SnapShot(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name=_(u'device'))
    timestamp = models.DateTimeField(_(u'timestamp'), auto_now_add=True)
    value = models.IntegerField(_(u'value'))

    class Meta:
        verbose_name = "SnapShot"
        verbose_name_plural = "SnapShots"

    def __str__(self):
        return f"{self.device} - {self.timestamp} - {self.value}"
