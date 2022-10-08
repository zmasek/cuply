import telegram
from django.test import TestCase
from unittest.mock import patch
from .factories import MicrocontrollerFactory, DeviceFactory
from ..choices import FSMClass, Category
from ..fsm import DigitalActuator, AnalogSensor, I2C, PWM
from ..telebot import bot, CHANNEL


class DigitalActuatorTestCase(TestCase):
    def setUp(self):
        self.microcontroller = MicrocontrollerFactory()
        self.device = DeviceFactory(microcontroller=self.microcontroller, blob={"state": "off"}, fsm_class=FSMClass.DIGITAL_ACTUATOR)
        self.digital_actuator = DigitalActuator(self.microcontroller, self.device)

    def test_no_children(self):
        self.assertEqual(self.digital_actuator.microcontroller, self.microcontroller)
        self.assertEqual(self.digital_actuator.device, self.device)
        self.assertEqual(self.digital_actuator.children, [])
        
    def test_with_children(self):
        device = DeviceFactory(parent=self.device)
        children = self.device.get_children()
        digital_actuator = DigitalActuator(self.microcontroller, self.device, children)
        self.assertEqual(digital_actuator.microcontroller, self.microcontroller)
        self.assertEqual(digital_actuator.device, self.device)
        self.assertEqual(digital_actuator.children, children)
        self.assertTrue(device.name in digital_actuator.__dict__)

    def test_serialization_serialize(self):
        result = self.digital_actuator.save()
        self.assertEqual(result, {"state": "off"})

    def test_serialization__restore_on(self):
        blob = {"state": "on"}
        result = self.digital_actuator._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_off(self):
        blob = {"state": "off"}
        result = self.digital_actuator._restore(blob)
        self.assertTrue(result is None)

    def test_serialization_init_from_blob_without_children(self):
        blob = {"state": "on"}
        with patch.object(DigitalActuator, "_restore"):
            digital_actuator = DigitalActuator.from_blob(blob, self.microcontroller, self.device)
            digital_actuator._restore.assert_called_once()
        self.assertTrue(isinstance(digital_actuator, DigitalActuator))

    def test_serialization_init_from_blob_with_children(self):
        blob = {"state": "on"}
        device = DeviceFactory(parent=self.device)
        children = self.device.get_children()
        with patch.object(DigitalActuator, "_restore"):
            digital_actuator = DigitalActuator.from_blob(blob, self.microcontroller, self.device, children)
            digital_actuator._restore.assert_called_once()
        self.assertTrue(isinstance(digital_actuator, DigitalActuator))

    def test_rules(self):
        # initial state should be off
        result = self.digital_actuator.save()
        self.assertEqual(result, {"state": "off"})
        # off.upon(decrease, enter=off, outputs=[report_state], collector=itemgetter(0))
        result = self.digital_actuator.decrease()
        self.assertEqual(result, "off")
        # off.upon(increase, enter=on, outputs=[save_state, make_on], collector=itemgetter(0))
        with patch.object(self.device, "write_data") as mock_write_data, patch.object(self.digital_actuator.device, "save") as mock_save:
            result = self.digital_actuator.increase()
            self.assertEqual(result, "on")
            mock_write_data.assert_called_once_with(1, self.microcontroller)
            mock_save.assert_called_once()
        # on.upon(decrease, enter=off, outputs=[save_state, make_off], collector=itemgetter(0))
        with patch.object(self.device, "write_data") as mock_write_data, patch.object(self.digital_actuator.device, "save") as mock_save:
            result = self.digital_actuator.decrease()
            self.assertEqual(result, "off")
            mock_write_data.assert_called_once_with(0, self.microcontroller)
            mock_save.assert_called_once()
        # on.upon(increase, enter=on, outputs=[report_state], collector=itemgetter(0))
        # make it on first
        with patch.object(self.device, "write_data"), patch.object(self.digital_actuator.device, "save"):
            self.digital_actuator.increase()
        # now continue
        result = self.digital_actuator.increase()
        self.assertEqual(result, "on")
        # on.upon(query_value, enter=on, outputs=[read_value], collector=itemgetter(0))
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = True
            value = self.digital_actuator.query_value()
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, True)
        # off.upon(query_value, enter=off, outputs=[read_value], collector=itemgetter(0))
        # make it off first
        with patch.object(self.device, "write_data"), patch.object(self.digital_actuator.device, "save"):
            self.digital_actuator.decrease()
        # now continue
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = False
            value = self.digital_actuator.query_value()
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, False)


class AnalogSensorTestCase(TestCase):
    def setUp(self):
        self.microcontroller = MicrocontrollerFactory()
        self.device = DeviceFactory(microcontroller=self.microcontroller)
        self.analog_sensor = AnalogSensor(self.microcontroller, self.device)

    def test_no_children(self):
        self.assertEqual(self.analog_sensor.microcontroller, self.microcontroller)
        self.assertEqual(self.analog_sensor.device, self.device)
        self.assertEqual(self.analog_sensor.children, [])
        
    def test_with_children(self):
        device = DeviceFactory(parent=self.device)
        children = self.device.get_children()
        analog_sensor = AnalogSensor(self.microcontroller, self.device, children)
        self.assertEqual(analog_sensor.microcontroller, self.microcontroller)
        self.assertEqual(analog_sensor.device, self.device)
        self.assertEqual(analog_sensor.children, children)
        self.assertTrue(device.name in analog_sensor.__dict__)

    def test_serialization_serialize(self):
        result = self.analog_sensor.save()
        self.assertEqual(result, {"state": "medium"})

    def test_serialization__restore_very_low(self):
        blob = {"state": "very_low"}
        result = self.analog_sensor._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_low(self):
        blob = {"state": "low"}
        result = self.analog_sensor._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_medium(self):
        blob = {"state": "medium"}
        result = self.analog_sensor._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_high(self):
        blob = {"state": "high"}
        result = self.analog_sensor._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_very_high(self):
        blob = {"state": "very_high"}
        result = self.analog_sensor._restore(blob)
        self.assertTrue(result is None)

    def test_serialization_init_from_blob_without_children(self):
        blob = {"state": "medium"}
        with patch.object(AnalogSensor, "_restore"):
            analog_sensor = AnalogSensor.from_blob(blob, self.microcontroller, self.device)
            analog_sensor._restore.assert_called_once()
        self.assertTrue(isinstance(analog_sensor, AnalogSensor))

    def test_serialization_init_from_blob_with_children(self):
        blob = {"state": "medium"}
        # need to specify to avoid double calls
        device = DeviceFactory(parent=self.device, category="", fsm_class=FSMClass.I2C)
        children = self.device.get_children()
        with patch.object(AnalogSensor, "_restore"):
            analog_sensor = AnalogSensor.from_blob(blob, self.microcontroller, self.device, children)
            analog_sensor._restore.assert_called_once()
        self.assertTrue(isinstance(analog_sensor, AnalogSensor))

    def test_rules(self):
        # initial state should be medium
        result = self.analog_sensor.save()
        self.assertEqual(result, {"state": "medium"})
        # medium.upon(query_value, enter=medium, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.TEMPERATURE
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "medium"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertTrue(31 < value < 32)
        # humidity
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.HUMIDITY
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "medium"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 88)
        # light
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.LIGHT
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "medium"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 923)
        # medium.upon(decrease, enter=low, outputs=[save_state, turn_on], collector=itemgetter(0))
        with patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.decrease()
            self.assertEqual(result, "low")
            mock_save.assert_called_once()
        # low.upon(query_value, enter=low, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.TEMPERATURE
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertTrue(31 < value < 32)
        # humidity
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.HUMIDITY
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 88)
        # light
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.LIGHT
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 923)
        # low.upon(decrease, enter=very_low, outputs=[save_state, notify_user], collector=itemgetter(0))
        with patch.object(bot, "send_message") as mock_send_message, patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.decrease()
            self.assertEqual(result, "very_low")
            message = f'{self.analog_sensor.device.name} is {result}.'
            mock_send_message.assert_called_once_with(chat_id=CHANNEL, text=message, parse_mode=telegram.ParseMode.HTML)
            mock_save.assert_called_once()
        # very_low.upon(query_value, enter=very_low, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.TEMPERATURE
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "very_low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertTrue(31 < value < 32)
        # humidity
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.HUMIDITY
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "very_low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 88)
        # light
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.LIGHT
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "very_low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 923)
        # very_low.upon(decrease, enter=very_low, outputs=[report_state], collector=itemgetter(0))
        result = self.analog_sensor.decrease()
        self.assertEqual(result, "very_low")
        # very_low.upon(increase, enter=low, outputs=[save_state], collector=itemgetter(0))
        with patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.increase()
            self.assertEqual(result, "low")
            mock_save.assert_called_once()
        # low.upon(increase, enter=medium, outputs=[save_state, turn_off], collector=itemgetter(0))
        with patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.increase()
            self.assertEqual(result, "medium")
            mock_save.assert_called_once()
        # medium.upon(increase, enter=high, outputs=[save_state, turn_off], collector=itemgetter(0))
        with patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.increase()
            self.assertEqual(result, "high")
            mock_save.assert_called_once()
        # high.upon(query_value, enter=high, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.TEMPERATURE
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertTrue(31 < value < 32)
        # humidity
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.HUMIDITY
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 88)
        # light
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.LIGHT
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 923)
        # high.upon(increase, enter=very_high, outputs=[save_state, notify_user], collector=itemgetter(0))
        with patch.object(bot, "send_message") as mock_send_message, patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.increase()
            self.assertEqual(result, "very_high")
            message = f'{self.analog_sensor.device.name} is {result}.'
            mock_send_message.assert_called_once_with(chat_id=CHANNEL, text=message, parse_mode=telegram.ParseMode.HTML)
            mock_save.assert_called_once()
        # very_high.upon(query_value, enter=very_high, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.TEMPERATURE
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "very_high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertTrue(31 < value < 32)
        # humidity
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.HUMIDITY
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "very_high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 88)
        # light
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            self.analog_sensor.device.category = Category.LIGHT
            self.analog_sensor.device.save()
            value = self.analog_sensor.query_value()
            result = self.analog_sensor.save()
            self.assertEqual(result, {"state": "very_high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 923)
        # very_high.upon(increase, enter=very_high, outputs=[report_state], collector=itemgetter(0))
        result = self.analog_sensor.increase()
        self.assertEqual(result, "very_high")
        # very_high.upon(decrease, enter=high, outputs=[save_state], collector=itemgetter(0))
        with patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.decrease()
            self.assertEqual(result, "high")
            mock_save.assert_called_once()
        # high.upon(decrease, enter=medium, outputs=[save_state, turn_off], collector=itemgetter(0))
        with patch.object(self.analog_sensor.device, "save") as mock_save:
            result = self.analog_sensor.decrease()
            self.assertEqual(result, "medium")
            mock_save.assert_called_once()


class I2CTestCase(TestCase):
    def setUp(self):
        self.microcontroller = MicrocontrollerFactory()
        self.device = DeviceFactory(microcontroller=self.microcontroller, fsm_class=FSMClass.I2C)
        self.i2c = I2C(self.microcontroller, self.device)

    def test_no_children(self):
        self.assertEqual(self.i2c.microcontroller, self.microcontroller)
        self.assertEqual(self.i2c.device, self.device)
        self.assertEqual(self.i2c.children, [])
        
    def test_with_children(self):
        device = DeviceFactory(parent=self.device)
        children = self.device.get_children()
        i2c = I2C(self.microcontroller, self.device, children)
        self.assertEqual(i2c.microcontroller, self.microcontroller)
        self.assertEqual(i2c.device, self.device)
        self.assertEqual(i2c.children, children)
        self.assertTrue(device.name in i2c.__dict__)

    def test_serialization_serialize(self):
        result = self.i2c.save()
        self.assertEqual(result, {"state": "medium"})

    def test_serialization__restore_very_low(self):
        blob = {"state": "very_low"}
        result = self.i2c._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_low(self):
        blob = {"state": "low"}
        result = self.i2c._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_medium(self):
        blob = {"state": "medium"}
        result = self.i2c._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_high(self):
        blob = {"state": "high"}
        result = self.i2c._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_very_high(self):
        blob = {"state": "very_high"}
        result = self.i2c._restore(blob)
        self.assertTrue(result is None)

    def test_serialization_init_from_blob_without_children(self):
        blob = {"state": "medium"}
        with patch.object(I2C, "_restore"):
            i2c = I2C.from_blob(blob, self.microcontroller, self.device)
            i2c._restore.assert_called_once()
        self.assertTrue(isinstance(i2c, I2C))

    def test_serialization_init_from_blob_with_children(self):
        blob = {"state": "medium"}
        device = DeviceFactory(parent=self.device)
        children = self.device.get_children()
        with patch.object(I2C, "_restore"):
            i2c = I2C.from_blob(blob, self.microcontroller, self.device, children)
            i2c._restore.assert_called_once()
        self.assertTrue(isinstance(i2c, I2C))

    def test_rules(self):
        # initial state should be medium
        result = self.i2c.save()
        self.assertEqual(result, {"state": "medium"})
        # medium.upon(query_value, enter=medium, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            value = self.i2c.query_value()
            result = self.i2c.save()
            self.assertEqual(result, {"state": "medium"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 100)
        # medium.upon(decrease, enter=low, outputs=[save_state, turn_on], collector=itemgetter(0))
        with patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.decrease()
            self.assertEqual(result, "low")
            mock_save.assert_called_once()
        # low.upon(query_value, enter=low, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            value = self.i2c.query_value()
            result = self.i2c.save()
            self.assertEqual(result, {"state": "low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 100)
        # low.upon(decrease, enter=very_low, outputs=[save_state, notify_user], collector=itemgetter(0))
        with patch.object(bot, "send_message") as mock_send_message, patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.decrease()
            self.assertEqual(result, "very_low")
            message = f'{self.i2c.device.name} is {result}.'
            mock_send_message.assert_called_once_with(chat_id=CHANNEL, text=message, parse_mode=telegram.ParseMode.HTML)
            mock_save.assert_called_once()
        # very_low.upon(query_value, enter=very_low, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            value = self.i2c.query_value()
            result = self.i2c.save()
            self.assertEqual(result, {"state": "very_low"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 100)
        # very_low.upon(decrease, enter=very_low, outputs=[report_state], collector=itemgetter(0))
        result = self.i2c.decrease()
        self.assertEqual(result, "very_low")
        # very_low.upon(increase, enter=low, outputs=[save_state], collector=itemgetter(0))
        with patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.increase()
            self.assertEqual(result, "low")
            mock_save.assert_called_once()
        # low.upon(increase, enter=medium, outputs=[save_state, turn_off], collector=itemgetter(0))
        with patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.increase()
            self.assertEqual(result, "medium")
            mock_save.assert_called_once()
        # medium.upon(increase, enter=high, outputs=[save_state, turn_off], collector=itemgetter(0))
        with patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.increase()
            self.assertEqual(result, "high")
            mock_save.assert_called_once()
        # high.upon(query_value, enter=high, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            value = self.i2c.query_value()
            result = self.i2c.save()
            self.assertEqual(result, {"state": "high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 100)
        # high.upon(increase, enter=very_high, outputs=[save_state, notify_user], collector=itemgetter(0))
        with patch.object(bot, "send_message") as mock_send_message, patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.increase()
            self.assertEqual(result, "very_high")
            message = f'{self.i2c.device.name} is {result}.'
            mock_send_message.assert_called_once_with(chat_id=CHANNEL, text=message, parse_mode=telegram.ParseMode.HTML)
            mock_save.assert_called_once()
        # very_high.upon(query_value, enter=very_high, outputs=[read_value], collector=itemgetter(0))
        # temperature
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 100
            value = self.i2c.query_value()
            result = self.i2c.save()
            self.assertEqual(result, {"state": "very_high"})
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 100)
        # very_high.upon(increase, enter=very_high, outputs=[report_state], collector=itemgetter(0))
        result = self.i2c.increase()
        self.assertEqual(result, "very_high")
        # very_high.upon(decrease, enter=high, outputs=[save_state], collector=itemgetter(0))
        with patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.decrease()
            self.assertEqual(result, "high")
            mock_save.assert_called_once()
        # high.upon(decrease, enter=medium, outputs=[save_state, turn_off], collector=itemgetter(0))
        with patch.object(self.i2c.device, "save") as mock_save:
            result = self.i2c.decrease()
            self.assertEqual(result, "medium")
            mock_save.assert_called_once()

class PWMTestCase(TestCase):
    def setUp(self):
        self.microcontroller = MicrocontrollerFactory()
        self.device = DeviceFactory(microcontroller=self.microcontroller, blob={"state": "closed"}, fsm_class=FSMClass.PWM)
        self.pwm = PWM(self.microcontroller, self.device)

    def test_no_children(self):
        self.assertEqual(self.pwm.microcontroller, self.microcontroller)
        self.assertEqual(self.pwm.device, self.device)
        self.assertEqual(self.pwm.children, [])
        
    def test_with_children(self):
        device = DeviceFactory(parent=self.device)
        children = self.device.get_children()
        pwm = PWM(self.microcontroller, self.device, children)
        self.assertEqual(pwm.microcontroller, self.microcontroller)
        self.assertEqual(pwm.device, self.device)
        self.assertEqual(pwm.children, children)
        self.assertTrue(device.name in pwm.__dict__)

    def test_serialization_serialize(self):
        result = self.pwm.save()
        self.assertEqual(result, {"state": "closed"})

    def test_serialization__restore_closed(self):
        blob = {"state": "closed"}
        result = self.pwm._restore(blob)
        self.assertTrue(result is None)

    def test_serialization__restore_open(self):
        blob = {"state": "opened"}
        result = self.pwm._restore(blob)
        self.assertTrue(result is None)

    def test_serialization_init_from_blob_without_children(self):
        blob = {"state": "closed"}
        with patch.object(PWM, "_restore"):
            pwm = PWM.from_blob(blob, self.microcontroller, self.device)
            pwm._restore.assert_called_once()
        self.assertTrue(isinstance(pwm, PWM))

    def test_serialization_init_from_blob_with_children(self):
        blob = {"state": "closed"}
        device = DeviceFactory(parent=self.device)
        children = self.device.get_children()
        with patch.object(PWM, "_restore"):
            pwm = PWM.from_blob(blob, self.microcontroller, self.device, children)
            pwm._restore.assert_called_once()
        self.assertTrue(isinstance(pwm, PWM))

    def test_rules(self):
        # initial state should be closed
        result = self.pwm.save()
        self.assertEqual(result, {"state": "closed"})
        # closed.upon(decrease, enter=closed, outputs=[report_state], collector=itemgetter(0))
        result = self.pwm.decrease()
        self.assertEqual(result, "closed")
        # closed.upon(increase, enter=opened, outputs=[save_state, make_opened], collector=itemgetter(0))
        with patch.object(self.device, "write_data") as mock_write_data, patch.object(self.pwm.device, "save") as mock_save:
            result = self.pwm.increase()
            self.assertEqual(result, "opened")
            mock_write_data.assert_called_once_with(164, self.microcontroller)
            mock_save.assert_called_once()
        # opened.upon(decrease, enter=closed, outputs=[save_state, make_closed], collector=itemgetter(0))
        with patch.object(self.device, "write_data") as mock_write_data, patch.object(self.pwm.device, "save") as mock_save:
            result = self.pwm.decrease()
            self.assertEqual(result, "closed")
            mock_write_data.assert_called_once_with(0, self.microcontroller)
            mock_save.assert_called_once()
        # opened.upon(increase, enter=opened, outputs=[report_state], collector=itemgetter(0))
        # make it opened first
        with patch.object(self.device, "write_data"), patch.object(self.pwm.device, "save"):
            self.pwm.increase()
        # now continue
        result = self.pwm.increase()
        self.assertEqual(result, "opened")
        # opened.upon(query_value, enter=opened, outputs=[read_value], collector=itemgetter(0))
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 10
            value = self.pwm.query_value()
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 10)
        # closed.upon(query_value, enter=closed, outputs=[read_value], collector=itemgetter(0))
        # make it closed first
        with patch.object(self.device, "write_data"):
            self.pwm.decrease()
        # now continue
        with patch.object(self.device, "read_data") as mock_read_data:
            mock_read_data.return_value = 10
            value = self.pwm.query_value()
            mock_read_data.assert_called_once_with(self.microcontroller)
            self.assertEqual(value, 10)
