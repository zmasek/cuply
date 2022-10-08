import copy
import datetime
from unittest.mock import patch
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.utils import timezone
from .factories import MicrocontrollerFactory, DeviceFactory
from ..fsm import AnalogSensor
from ..loop_manager import GreenHouseManager, DELAY, q, DELTA_INPUT
from ..models import Device, SnapShot


class GreenHouseManagerTestCase(TestCase):
    def setUp(self):
        self.microcontroller = MicrocontrollerFactory()
        device_1 = DeviceFactory(microcontroller=self.microcontroller)
        device_2 = DeviceFactory(microcontroller=self.microcontroller, parent=device_1)
        self.devices = Device.objects.all()
        with patch.object(self.microcontroller, "start") as mock_start:
            self.green_house_manager = GreenHouseManager(self.microcontroller, self.devices)

    def test_setup_readings_passed_during_init(self):
        self.assertEqual(len(self.green_house_manager.readings), 2)
        self.assertEqual(self.green_house_manager.readings[0]["parent"], None)
        self.assertEqual(self.green_house_manager.readings[0]["name"], self.devices[0].name)
        self.assertEqual(self.green_house_manager.readings[0]["kind"], self.devices[0].get_kind())
        self.assertTrue(isinstance(self.green_house_manager.readings[0]["fsm_instance"], AnalogSensor))
        self.assertTrue(isinstance(self.green_house_manager.readings[0]["median_old"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[0]["median"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[0]["archive"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[0]["old"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[0]["new"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[0]["timestamp"], datetime.datetime))
        self.assertEqual(self.green_house_manager.readings[0]["state"], "medium")
        self.assertEqual(self.green_house_manager.readings[1]["parent"], self.devices[0].name)
        self.assertEqual(self.green_house_manager.readings[1]["name"], self.devices[1].name)
        self.assertEqual(self.green_house_manager.readings[1]["kind"], self.devices[1].get_kind())
        self.assertTrue(isinstance(self.green_house_manager.readings[1]["fsm_instance"], AnalogSensor))
        self.assertTrue(isinstance(self.green_house_manager.readings[1]["median_old"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[1]["median"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[1]["archive"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[1]["old"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[1]["new"], float))
        self.assertTrue(isinstance(self.green_house_manager.readings[1]["timestamp"], datetime.datetime))
        self.assertEqual(self.green_house_manager.readings[1]["state"], "medium")

    def test_is_value_increasing_increasing(self):
        reading = {"median": 38.0 ,"median_old": 37.0}
        result = self.green_house_manager.is_value_increasing(reading)
        self.assertTrue(result)

    def test_is_value_increasing_decreasing(self):
        reading = {"median": 37.0 ,"median_old": 38.0}
        result = self.green_house_manager.is_value_increasing(reading)
        self.assertFalse(result)

    def test_is_value_increasing_no(self):
        reading = {"median": 37.0 ,"median_old": 37.0}
        result = self.green_house_manager.is_value_increasing(reading)
        self.assertIsNone(result)
        
    def test_can_proceed_true(self):
        timestamp = timezone.now() - DELAY
        result = self.green_house_manager.can_proceed(timestamp)
        self.assertTrue(result)

    def test_can_proceed_false(self):
        timestamp = timezone.now()
        result = self.green_house_manager.can_proceed(timestamp)
        self.assertFalse(result)

    def test_will_state_change_yes(self):
        reading = {
            "fsm_instance": self.green_house_manager.readings[0]["fsm_instance"],
            "state": "medium",
            "median": 37.0,
        }
        result = self.green_house_manager.will_state_change(reading)
        self.assertTrue(result)

    def test_will_state_change_no(self):
        reading = {
            "fsm_instance": self.green_house_manager.readings[0]["fsm_instance"],
            "state": "medium",
            "median": 500.0,
        }
        result = self.green_house_manager.will_state_change(reading)
        self.assertFalse(result)

    @patch("common.loop_manager.timezone")
    def test_within_range_yes(self, mock_timezone):
        now = timezone.now()
        now = now.replace(hour=20)
        time_now = timezone.datetime.time(now)
        mock_timezone.datetime.time.return_value = time_now
        fsm = self.green_house_manager.readings[0]["fsm_instance"]
        result = self.green_house_manager.within_range(fsm)
        self.assertTrue(result)

    @patch("common.loop_manager.timezone")
    def test_within_range_no(self, mock_timezone):
        now = timezone.now()
        now = now.replace(hour=22)
        time_now = timezone.datetime.time(now)
        mock_timezone.datetime.time.return_value = time_now
        fsm = self.green_house_manager.readings[0]["fsm_instance"]
        result = self.green_house_manager.within_range(fsm)
        self.assertFalse(result)

    def test_update_devices_queue_empty(self):
        q.queue.clear()
        with patch.object(self.green_house_manager, "setup_readings") as mock_setup_readings:
            self.green_house_manager.update_devices()
            mock_setup_readings.assert_not_called()

    def test_update_devices_queue_full(self):
        q.queue.clear()
        DeviceFactory(microcontroller=self.microcontroller)
        self.assertEqual(self.green_house_manager.devices.count(), 2)
        with patch.object(self.green_house_manager, "setup_readings") as mock_setup_readings:
            self.green_house_manager.update_devices()
            mock_setup_readings.assert_called_once()
        self.assertEqual(self.green_house_manager.devices.count(), 3)

    def test_update_readings(self):
        initial_readings = self.green_house_manager.readings
        for reading in initial_readings:
            self.assertEqual(reading['archive'], 34.0)
            self.assertEqual(reading['old'], 34.0)
            self.assertEqual(reading['new'], 34.0)
            self.assertEqual(reading['median_old'], 34.0)
            self.assertEqual(reading['median'], 34.0)
        with patch.object(initial_readings[0]["fsm_instance"], "query_value") as mock_query_value_1, patch.object(initial_readings[1]["fsm_instance"], "query_value") as mock_query_value_2:
            mock_query_value_1.return_value = 20.0
            mock_query_value_2.return_value = 20.0
            self.green_house_manager.update_readings()
            mock_query_value_1.assert_called_once()
            mock_query_value_2.assert_called_once()
        updated_readings = self.green_house_manager.readings
        for reading in updated_readings:
            self.assertEqual(reading['archive'], 34.0)
            self.assertEqual(reading['old'], 34.0)
            self.assertEqual(reading['new'], 20.0)
            self.assertEqual(reading['median_old'], 34.0)
            self.assertEqual(reading['median'], 34.0)

    def test_run_inputs_value_stays(self):
        self.green_house_manager.readings = [self.green_house_manager.readings[0]]
        old_readings = self.green_house_manager.readings
        old_timestamp = copy.deepcopy(old_readings[0]["timestamp"])
        self.green_house_manager.timestamp_input -= datetime.timedelta(seconds=DELTA_INPUT+1)
        with (
            patch.object(self.green_house_manager, "can_proceed") as mock_can_proceed,
            patch.object(self.green_house_manager, "will_state_change") as mock_will_state_change,
            patch.object(self.green_house_manager, "within_range") as mock_within_range,
            patch.object(self.green_house_manager, "is_value_increasing") as mock_is_value_increasing,
            patch.object(self.green_house_manager.readings[0]["fsm_instance"], "increase") as mock_increase,
            patch.object(self.green_house_manager.readings[0]["fsm_instance"], "decrease") as mock_decrease,
        ):
            mock_can_proceed.return_value = True
            mock_will_state_change.return_value = True
            mock_within_range.return_value = True
            mock_is_value_increasing.return_value = None
            self.green_house_manager.run_inputs()
            mock_increase.assert_not_called()
            mock_decrease.assert_not_called()
        self.assertNotEqual(old_timestamp, self.green_house_manager.readings[0]["timestamp"])

    def test_run_inputs_value_increases(self):
        self.green_house_manager.readings = [self.green_house_manager.readings[0]]
        old_readings = self.green_house_manager.readings
        old_timestamp = copy.deepcopy(old_readings[0]["timestamp"])
        self.green_house_manager.timestamp_input -= datetime.timedelta(seconds=DELTA_INPUT+1)
        with (
            patch.object(self.green_house_manager, "can_proceed") as mock_can_proceed,
            patch.object(self.green_house_manager, "will_state_change") as mock_will_state_change,
            patch.object(self.green_house_manager, "within_range") as mock_within_range,
            patch.object(self.green_house_manager, "is_value_increasing") as mock_is_value_increasing,
            patch.object(self.green_house_manager.readings[0]["fsm_instance"], "increase") as mock_increase,
            patch.object(self.green_house_manager.readings[0]["fsm_instance"], "decrease") as mock_decrease,
        ):
            mock_can_proceed.return_value = True
            mock_will_state_change.return_value = True
            mock_within_range.return_value = True
            mock_is_value_increasing.return_value = True
            self.green_house_manager.run_inputs()
            mock_increase.assert_called_once()
            mock_decrease.assert_not_called()
        self.assertNotEqual(old_timestamp, self.green_house_manager.readings[0]["timestamp"])


    def test_run_inputs_value_decreases(self):
        self.green_house_manager.readings = [self.green_house_manager.readings[0]]
        old_readings = self.green_house_manager.readings
        old_timestamp = copy.deepcopy(old_readings[0]["timestamp"])
        self.green_house_manager.timestamp_input -= datetime.timedelta(seconds=DELTA_INPUT+1)
        with (
            patch.object(self.green_house_manager, "can_proceed") as mock_can_proceed,
            patch.object(self.green_house_manager, "will_state_change") as mock_will_state_change,
            patch.object(self.green_house_manager, "within_range") as mock_within_range,
            patch.object(self.green_house_manager, "is_value_increasing") as mock_is_value_increasing,
            patch.object(self.green_house_manager.readings[0]["fsm_instance"], "increase") as mock_increase,
            patch.object(self.green_house_manager.readings[0]["fsm_instance"], "decrease") as mock_decrease,
        ):
            mock_can_proceed.return_value = True
            mock_will_state_change.return_value = True
            mock_within_range.return_value = True
            mock_is_value_increasing.return_value = False
            self.green_house_manager.run_inputs()
            mock_increase.assert_not_called()
            mock_decrease.assert_called_once()
        self.assertNotEqual(old_timestamp, self.green_house_manager.readings[0]["timestamp"])

    @patch("common.loop_manager.async_to_sync")
    @patch("json.dumps")
    def test_communicate_state(self, mock_dumps, mock_async_to_sync):
        self.green_house_manager.communicate_state()
        clean_readings = []
        for reading in self.green_house_manager.readings:
            clean_readings.append({key: value for key, value in reading.items() if key != "fsm_instance"})
        mock_dumps.assert_called_once_with(clean_readings, cls=DjangoJSONEncoder)
        mock_async_to_sync.assert_called_once_with(self.green_house_manager.channel_layer.group_send)

    def test_save_snapshot(self):
        self.assertFalse(SnapShot.objects.exists())
        old_timestamp = timezone.now()
        old_timestamp = old_timestamp.replace(year=self.green_house_manager.timestamp_snapshot.year - 1)
        self.green_house_manager.timestamp_snapshot = old_timestamp
        self.green_house_manager.save_snapshot()
        self.assertEqual(SnapShot.objects.count(), 2)
        for reading in self.green_house_manager.readings:
            device = Device.objects.get(name=reading["name"])
            snapshot = SnapShot.objects.get(device=device)
            self.assertTrue(snapshot.timestamp)
            self.assertEqual(snapshot.value, reading["median"])
