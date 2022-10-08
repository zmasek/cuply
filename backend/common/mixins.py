# The Mixin classes are extending the models with the non-DB members
from arduino import Arduino
import time


class MicrocontrollerMixin(object):
    def __init__(self, *args, **kwargs):
        super(MicrocontrollerMixin, self).__init__(*args, **kwargs)
        self._devices = None
        self._microcontroller = None

    def _register_devices(self):
        self._devices = [device.pin for device in self.device_set.all() if device.pin]
        self._microcontroller.output(self._devices)

    def start(self):
        self._microcontroller = Arduino(self.path)
        time.sleep(1)
        self._register_devices()
        time.sleep(1)

    def restart(self):
        self.stop()
        self.start()

    def stop(self):
        if self._microcontroller:
            self.flush()
            self._microcontroller.close()
            self._microcontroller = None

    def flush(self):
        if self._microcontroller:
            self._microcontroller.serial.setDTR(False)
            time.sleep(2)
            self._microcontroller.serial.reset_input_buffer()
            self._microcontroller.serial.setDTR(True)
            # self._microcontroller.serial.flush()
            # self._microcontroller.serial.reset_input_buffer()
            # self._microcontroller.serial.reset_output_buffer()

    def read_data(self, device):
        if device.fsm_class == 'PWM':
            return int(self._microcontroller.readServo())
        elif device.fsm_class == "I2C":
            return int(self._microcontroller.i2cRead())
        elif device.fsm_class == 'AnalogSensor':
            try:
                return int(self._microcontroller.analogRead(device.pin))
            except Exception as e:
                return 0
        elif device.fsm_class == "DigitalActuator":
            return self._microcontroller.getState(device.pin)

    def write_data(self, value, device):
        if device.fsm_class == 'PWM':
            self._microcontroller.moveServo(value)
        elif device.fsm_class == "AnalogSensor":
            self._microcontroller.analogWrite(device.pin, value)
        else:
            if value > 0:
                self._microcontroller.setHigh(device.pin)
            else:
                self._microcontroller.setLow(device.pin)
        return value


class DeviceMixin(object):
    def read_data(self, microcontroller):
        return microcontroller.read_data(self)

    def write_data(self, value, microcontroller):
        return microcontroller.write_data(value, self)
