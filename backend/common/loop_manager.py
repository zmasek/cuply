import datetime
import json
import queue
import statistics
import time
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import SnapShot, Device

DELAY = datetime.timedelta(seconds=2)  # how often to query for the readings
DELTA_SNAPSHOT = 300  # how often to save the snapshot for the trend graphs, 300 seconds, 5 minutes
DELTA_INPUT = 3  # how often to run the inputs, 3 seconds
q = queue.Queue()  # global queue accessible from other threads (the signals from main Django thread)


class GreenHouseManager:
    def __init__(self, microcontroller, devices):
        """
            Initialize the manager:
                - the channel layer for Django channels
                - start the passing microcontroller (should be a setting instead)
                - setup all the devices with all the information previously saved in the DB
                - as well as the associated readings
                - initialize the starting timestamp
        """
        self.channel_layer = get_channel_layer()
        self.microcontroller = microcontroller
        self.microcontroller.start()
        self.devices = devices
        self.readings = self.setup_readings()
        self.timestamp_snapshot = timezone.now()
        self.timestamp_input = timezone.now()

    def setup_readings(self):
        """Setup all readings according to the each device passed to the manager so they are
        regularly updated against the state of the system.
        """
        readings = []
        for device in self.devices:
            fsm_instance = device.get_fsm(self.microcontroller)
            value = fsm_instance.query_value()
            parent = None
            if device.parent is not None:
                parent = device.parent.name
            readings.append({
                "parent": parent,
                "name": device.name,
                "kind": device.get_kind(),
                "fsm_instance": fsm_instance,
                "median_old": value,
                "median": value,
                "archive": value,
                "old": value,
                "new": value,
                "timestamp": timezone.now(),
                "state": device.blob["state"]
            })
        return readings

    def is_value_increasing(self, reading):
        """ Return True if the value is increasing, False if decreasing and None
        if it stays the same.
        """
        if reading["median"] > reading["median_old"]:
            return True
        elif reading["median"] < reading["median_old"]:
            return False

    def can_proceed(self, timestamp):
        """Return if enough time has passed."""
        return timezone.now() - timestamp > DELAY

    def will_state_change(self, reading):
        """Return boolean if the state is meant to change according to the set up thresholds for the device.
        """
        device = reading["fsm_instance"].device
        fsm_threshold = device.thresholds[reading["state"]]
        return not (fsm_threshold[0] <= reading["median"] <= fsm_threshold[1])

    def within_range(self, fsm):
        """Return boolean if the current time falls between before and after times set for the device.
        """
        return (
            fsm.device.after <=
            timezone.datetime.time(timezone.now()) <=
            fsm.device.before
        )


    def run(self):
        """
            The main event loop which controls:
                - adding or removing the devices
                - the environment readings
                - state changes on the actuators depending on the sensor readings
                - communicating state to the websocket
                - storing the snapshot of the state for trend graphs
        """
        while True:
            self.update_devices()
            self.update_readings()
            self.run_inputs()
            self.communicate_state()
            self.save_snapshot()

    def update_devices(self):
        """q is a global queue that multiple threads have access to. The signal will update the queue
        and in turn, in the event loop, things are refreshed immediately.
        """
        if not q.empty():
            obj = q.get()
            # ORM can do a much better job than to handle pure python lists here so
            # there's no logic that would update the python list of model instances
            # the signals send the correct object and operation regardless
            self.devices = Device.objects.all()
            # refresh readings
            self.readings = self.setup_readings()
            q.task_done()

    def update_readings(self):
        """Retrieve the readings from the sensors and store them in the instance dictionary.
        """
        for reading in self.readings:
            reading['archive'] = reading['old']
            reading['old'] = reading['new']
            reading['new'] = reading["fsm_instance"].query_value()
            reading['median_old'] = reading['median']
            # normalize median value for readings to eliminate the outliers
            reading['median'] = statistics.median([
                reading['archive'], reading['old'], reading['new']
            ])


    def run_inputs(self):
        """For each sensor in the readings member, because the design is such that sensors trigger children, a number of checks are
        executed to see if the state machine can be triggered to change.
        """
        now = timezone.now()
        delta = now - self.timestamp_input
        if delta.total_seconds() > DELTA_INPUT:
            self.timestamp_input = now
            for reading in [value for value in self.readings if value["kind"] == "sensor"]:
                if self.can_proceed(reading['timestamp']) and self.will_state_change(reading) and self.within_range(reading["fsm_instance"]):
                    value_state = self.is_value_increasing(reading)
                    if value_state is True:
                        state = reading["fsm_instance"].increase()
                    elif value_state is False:
                        state = reading["fsm_instance"].decrease()
                    else:
                        state = reading["state"]
                    reading["state"] = state
                    reading['timestamp'] = timezone.now()
            # check root level actuators (time dependant code)
            for reading in [value for value in self.readings if value["kind"] == "actuator" and value["parent"] is None]:
                if self.can_proceed(reading['timestamp']):
                    current_state = reading["state"]
                    desired_state = reading["fsm_instance"].device.desired_state
                    if self.within_range(reading["fsm_instance"]):
                        if current_state != desired_state:
                            reading["state"] = reading["fsm_instance"].increase() if current_state == "off" else reading["fsm_instance"].decrease()
                            reading['timestamp'] = timezone.now()
                    else:
                        if current_state == desired_state:
                            reading["state"] = reading["fsm_instance"].increase() if current_state == "off" else reading["fsm_instance"].decrease()
                            reading['timestamp'] = timezone.now()

    def communicate_state(self):
        """Send the readings except the fsm_instance member to the websocket."""
        clean_readings = []
        for reading in self.readings:
            clean_readings.append({key: value for key, value in reading.items() if key != "fsm_instance"})
        message = json.dumps(clean_readings, cls=DjangoJSONEncoder)
        async_to_sync(self.channel_layer.group_send)('events', {'type': 'display.reading', 'message': message})

    def save_snapshot(self):
        """Create a new SnapShot instance in the database if enough time passed. They are used later for displaying trends.
        """
        now = timezone.now()
        delta = now - self.timestamp_snapshot
        if delta.total_seconds() > DELTA_SNAPSHOT:
            self.timestamp_snapshot = now
            for device in self.devices:
                if device.get_kind() == "sensor":
                    reading = [reading for reading in self.readings if reading["name"] == device.name][0]
                    SnapShot.objects.create(
                        device=device,
                        timestamp=reading["timestamp"],
                        value=reading["median"]
                    )
