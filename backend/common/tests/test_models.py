import random
from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch

from .factories import DeviceFactory, MicrocontrollerFactory, PlantFactory, SnapShotFactory, UserFactory

from ..choices import Category, FSMClass, ANALOG_SENSOR_BLOBS, DIGITAL_ACTUATOR_BLOBS, PWM_BLOBS, I2C_BLOBS
from ..models import default_blob, validate_attr_compatible


class MicrocontrollerTestCase(TestCase):
    def setUp(self):
        self.microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        
    def test___init__(self):
        self.microcontroller._devices is None
        self.microcontroller._microcontroller is None

    @patch("common.mixins.Arduino")
    def test___register_devices(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        self.microcontroller._register_devices()
        self.assertEqual(self.microcontroller._devices, [])
        self.microcontroller._microcontroller.output.called_once_with(self.microcontroller._devices)

    @patch("common.mixins.time")
    @patch("common.mixins.Arduino")
    def test_start(self, mock_Arduino, mock_time):
        self.microcontroller.start()
        self.assertEqual(self.microcontroller._microcontroller, mock_Arduino(self.microcontroller.path))
        self.assertEqual(mock_time.sleep.call_count, 2)
        self.assertEqual(self.microcontroller._devices, [])
        self.microcontroller._microcontroller.output.assert_called_once_with(self.microcontroller._devices)

    def test_stop_microcontroller(self):
        with patch.object(self.microcontroller, "flush"):
            self.microcontroller.stop()
            self.microcontroller.flush.called_once()
            self.assertEqual(self.microcontroller._microcontroller, None)
    
    def test_stop_no_microcontroller(self):
        self.microcontroller._microcontroller = None
        with patch.object(self.microcontroller, "flush"):
            self.microcontroller.stop()
            self.microcontroller.flush.not_called()

    def test_restart(self):
        with patch.object(self.microcontroller, "stop"), patch.object(self.microcontroller, "start"):
            self.microcontroller.restart()
            self.microcontroller.stop.called_once()
            self.microcontroller.start.called_once()

    @patch("common.mixins.time")
    def test_flush_no_microcontroller(self, mock_time):
        self.microcontroller._microcontroller = None
        self.microcontroller.flush()
        mock_time.sleep.assert_not_called()

    @patch("common.mixins.time")
    @patch("common.mixins.Arduino")
    def test_flush_microcontroller(self, mock_Arduino, mock_time):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        self.microcontroller.flush()
        self.assertEqual(self.microcontroller._microcontroller.serial.setDTR.call_count, 2)
        mock_time.sleep.called_once_with(2)
        self.microcontroller._microcontroller.serial.reset_input_buffer.called_once()

    @patch("common.mixins.Arduino")
    def test_read_data_pwm(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            blob=random.choice(PWM_BLOBS),
            fsm_class=FSMClass.PWM,
            name="Servo",
            pin="A0",
            microcontroller=self.microcontroller,
        )
        result = self.microcontroller.read_data(device)
        self.microcontroller._microcontroller.readServo.assert_called_once()

    @patch("common.mixins.Arduino")
    def test_read_data_i2c(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            fsm_class=FSMClass.I2C,
            name="WaterLevel",
            pin="A0",#?
            microcontroller=self.microcontroller,
        )
        result = self.microcontroller.read_data(device)
        self.microcontroller._microcontroller.i2cRead.assert_called_once()

    @patch("common.mixins.Arduino")
    def test_read_data_analogsensor(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            category=Category.TEMPERATURE,
            name="Temperature",
            pin="A0",
            microcontroller=self.microcontroller,
        )
        result = self.microcontroller.read_data(device)
        self.microcontroller._microcontroller.analogRead.assert_called_once_with(device.pin)

    @patch("common.mixins.Arduino")
    def test_read_data_analogsensor_exception(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            category=Category.TEMPERATURE,
            name="Temperature",
            pin="A0",
            microcontroller=self.microcontroller,
        )
        self.microcontroller._microcontroller.analogRead.return_value = "\n"
        result = self.microcontroller.read_data(device)
        self.assertEqual(result, 0)

    @patch("common.mixins.Arduino")
    def test_read_data_digitalactuator(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            blob=random.choice(DIGITAL_ACTUATOR_BLOBS),
            fsm_class=FSMClass.DIGITAL_ACTUATOR,
            name="Relay",
            pin="D1",
            microcontroller=self.microcontroller,
        )
        result = self.microcontroller.read_data(device)
        self.microcontroller._microcontroller.getState.assert_called_once_with(device.pin)

    @patch("common.mixins.Arduino")
    def test_write_data_pwm(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            blob=random.choice(PWM_BLOBS),
            fsm_class=FSMClass.PWM,
            name="Servo",
            pin="A0",#?
            microcontroller=self.microcontroller,
        )
        value = 1
        result = self.microcontroller.write_data(1, device)
        self.microcontroller._microcontroller.moveServo.assert_called_once_with(value)
    
    @patch("common.mixins.Arduino")
    def test_write_data_analogsensor(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            category=Category.TEMPERATURE,
            name="Temperature",
            pin="A0",
            microcontroller=self.microcontroller,
        )
        value = 1
        result = self.microcontroller.write_data(value, device)
        self.microcontroller._microcontroller.analogWrite.assert_called_once_with(device.pin, value)

    @patch("common.mixins.Arduino")
    def test_write_data_digitalactuator_on(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            blob=random.choice(DIGITAL_ACTUATOR_BLOBS),
            fsm_class=FSMClass.DIGITAL_ACTUATOR,
            name="Relay",
            pin="D1",
            microcontroller=self.microcontroller,
        )
        value = 1
        result = self.microcontroller.write_data(value, device)
        self.microcontroller._microcontroller.setHigh.assert_called_once_with(device.pin)

    @patch("common.mixins.Arduino")
    def test_write_data_digitalactuator_off(self, mock_Arduino):
        self.microcontroller._microcontroller = mock_Arduino(self.microcontroller.path)
        device = DeviceFactory(
            blob=random.choice(DIGITAL_ACTUATOR_BLOBS),
            fsm_class=FSMClass.DIGITAL_ACTUATOR,
            name="Relay",
            pin="D1",
            microcontroller=self.microcontroller,
        )
        value = 0
        result = self.microcontroller.write_data(value, device)
        self.microcontroller._microcontroller.setLow.assert_called_once_with(device.pin)


class DeviceTestCase(TestCase):
    def setUp(self):
        pass

    def test_default_blob(self):
        self.assertEqual(default_blob(), {"state": "medium"})

    def test_validate_attr_compabitle_identifier(self):
        value = "for"
        self.assertRaises(ValidationError, validate_attr_compatible, value)

    def test_validate_attr_compabitle_keyword(self):
        value = "1foo"
        self.assertRaises(ValidationError, validate_attr_compatible, value)

    def test_validate_attr_compabitle_success(self):
        value = "good"
        self.assertEqual(validate_attr_compatible(value), None)

    def test_read_data(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        device = DeviceFactory(
            category=Category.LIGHT,
            name="LightSensor",
            pin="A0",
            microcontroller=microcontroller,
        )
        with patch.object(microcontroller, "read_data"):
            device.read_data(microcontroller)
            device.microcontroller.read_data.assert_called_once_with(device)

    def test_write_data(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        device = DeviceFactory(
            category=Category.LIGHT,
            name="LightSensor",
            pin="A0",
            microcontroller=microcontroller,
        )
        with patch.object(microcontroller, "write_data"):
            value = 1
            device.write_data(value, microcontroller)
            device.microcontroller.write_data.assert_called_once_with(value, device)

    def test___str__(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        name = "LightSensor"
        device = DeviceFactory(
            category=Category.LIGHT,
            name=name,
            pin="A0",
            microcontroller=microcontroller,
        )
        self.assertEqual(device.__str__(), name)

    def test_get_fsm(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        device = DeviceFactory(
            category=Category.LIGHT,
            name="LightSensor",
            pin="A0",
            microcontroller=microcontroller,
        )
        result = device.get_fsm(microcontroller)
        self.assertEqual(type(result).__name__, "AnalogSensor")

    def test_get_kind_analogsensor(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        device = DeviceFactory(
            category=Category.LIGHT,
            name="LightSensor",
            pin="A0",
            microcontroller=microcontroller,
        )
        kind = device.get_kind()
        self.assertEqual(kind, "sensor")

    def test_get_kind_i2c(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        device = DeviceFactory(
            fsm_class=FSMClass.I2C,
            name="WaterLevel",
            pin="A0",
            microcontroller=microcontroller,
        )
        kind = device.get_kind()
        self.assertEqual(kind, "sensor")

    def test_get_kind_digitalactuator(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        device = DeviceFactory(
            blob=random.choice(DIGITAL_ACTUATOR_BLOBS),
            fsm_class=FSMClass.DIGITAL_ACTUATOR,
            name="WaterLevel",
            pin="A0",
            microcontroller=microcontroller,
        )
        kind = device.get_kind()
        self.assertEqual(kind, "actuator")

    def test_clean_bad_category(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        with self.assertRaises(ValidationError) as ex:
            DeviceFactory(
                category="",
                name="LightSensor",
                pin="A0",
                microcontroller=microcontroller,
            )
        self.assertEqual(ex.exception.messages[0], "AnalogSensor devices must have category set.")

    def test_clean_bad_analogsensor_blob(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        with self.assertRaises(ValidationError) as ex:
            DeviceFactory(
                blob=random.choice(PWM_BLOBS),
                name="LightSensor",
                pin="A0",
                microcontroller=microcontroller,
            )
        self.assertEqual(ex.exception.messages[0], f"AnalogSensor devices can have blobs from {ANALOG_SENSOR_BLOBS}.")


    def test_clean_bad_digitalactuator_blob(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        with self.assertRaises(ValidationError) as ex:
            DeviceFactory(
                fsm_class=FSMClass.DIGITAL_ACTUATOR,
                blob=random.choice(PWM_BLOBS),
                name="LightSensor",
                pin="A0",
                microcontroller=microcontroller,
            )
        self.assertEqual(ex.exception.messages[0], f"DigitalActuator devices can have blobs from {DIGITAL_ACTUATOR_BLOBS}.")

    def test_clean_bad_i2c_blob(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        with self.assertRaises(ValidationError) as ex:
            DeviceFactory(
                fsm_class=FSMClass.I2C,
                blob=random.choice(PWM_BLOBS),
                name="LightSensor",
                pin="A0",
                microcontroller=microcontroller,
            )
        self.assertEqual(ex.exception.messages[0], f"I2C devices can have blobs from {I2C_BLOBS}.")

    def test_clean_bad_pwm_blob(self):
        microcontroller = MicrocontrollerFactory(
            name="Arduino Due",
        )
        with self.assertRaises(ValidationError) as ex:
            DeviceFactory(
                fsm_class=FSMClass.PWM,
                blob=random.choice(DIGITAL_ACTUATOR_BLOBS),
                name="LightSensor",
                pin="A0",
                microcontroller=microcontroller,
            )
        self.assertEqual(ex.exception.messages[0], f"PWM devices can have blobs from {PWM_BLOBS}.")


class PlantTestCase(TestCase):
    def setUp(self):
        self.plant = PlantFactory()

    def test___str__(self):
        self.assertEqual(self.plant.__str__(), self.plant.name)


class ProfileTestCase(TestCase):
    def setUp(self):
        user = UserFactory()
        self.profile = user.profile

    def test___str__(self):
        self.assertEqual(self.profile.__str__(), f"Profile - {self.profile.user.get_full_name()}")


class SnapShotTestCase(TestCase):
    def setUp(self):
        self.snapshot = SnapShotFactory()

    def test___str__(self):
        self.assertEqual(self.snapshot.__str__(), f"{self.snapshot.device} - {self.snapshot.timestamp} - {self.snapshot.value}")
