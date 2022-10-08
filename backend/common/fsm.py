import telegram
from operator import itemgetter
from automat import MethodicalMachine
from .utils import invert_analog_value, normalize_value
from .telebot import bot, CHANNEL
from .choices import Category


class DigitalActuator:
    _machine = MethodicalMachine()

    def __init__(self, microcontroller, device, children=None):
        self.microcontroller = microcontroller
        self.device = device
        self.children = children if children is not None else []
        for child in self.children:
            setattr(self, child.name, child.get_fsm(microcontroller))

    # INPUTS
    @_machine.input()
    def query_value(self):
        pass

    @_machine.input()
    def increase(self):
        pass

    @_machine.input()
    def decrease(self):
        pass

    # OUTPUTS
    @_machine.output()
    def report_state(self):
        blob = self.save()
        return blob["state"]

    @_machine.output()
    def save_state(self):
        self.device.blob = self.save()
        self.device.save()
        return self.device.blob["state"]

    @_machine.output()
    def read_value(self):
        return self.device.read_data(self.microcontroller)

    # SERIALIZATION
    @_machine.serializer()
    def save(self, state):
        return {"state": state}

    @_machine.unserializer()
    def _restore(self, blob):
        return blob["state"]

    @classmethod
    def from_blob(cls, blob, microcontroller, device, children=None):
        self = cls(microcontroller, device, children)
        self._restore(blob)
        return self

    # STATES
    @_machine.state(serialized="off", initial=True)
    def off(self):
        pass

    @_machine.state(serialized="on")
    def on(self):
        pass

    # OUTPUTS
    @_machine.output()
    def make_off(self):
        return self.device.write_data(0, self.microcontroller)

    @_machine.output()
    def make_on(self):
        return self.device.write_data(1, self.microcontroller)

    # RULES (for changing the state and saving it)
    off.upon(increase, enter=on, outputs=[save_state, make_on], collector=itemgetter(0))
    on.upon(decrease, enter=off, outputs=[save_state, make_off], collector=itemgetter(0))

    # avoid exception, make it invariant
    off.upon(decrease, enter=off, outputs=[report_state], collector=itemgetter(0))
    on.upon(increase, enter=on, outputs=[report_state], collector=itemgetter(0))

    # query value (read input, but the state remains)
    on.upon(query_value, enter=on, outputs=[read_value], collector=itemgetter(0))
    off.upon(query_value, enter=off, outputs=[read_value], collector=itemgetter(0))


class AnalogSensor:
    _machine = MethodicalMachine()

    def __init__(self, microcontroller, device, children=None):
        self.device = device
        self.microcontroller = microcontroller
        self.children = children if children is not None else []
        for child in self.children:
            setattr(self, child.name, child.get_fsm(microcontroller))

    # INPUTS
    @_machine.input()
    def query_value(self):
        pass

    @_machine.input()
    def increase(self):
        pass

    @_machine.input()
    def decrease(self):
        pass

    # OUTPUTS
    @_machine.output()
    def report_state(self):
        blob = self.save()
        return blob["state"]

    @_machine.output()
    def save_state(self):
        self.device.blob = self.save()
        self.device.save()
        return self.device.blob["state"]

    @_machine.output()
    def read_value(self):
        value = invert_analog_value(self.device.read_data(self.microcontroller))
        if self.device.category == Category.HUMIDITY:
            value = (value / 1023) * 3000
            value = ((value - 0.958) / 0.0307) / 1000
            value = int(value)
        elif self.device.category == Category.TEMPERATURE:
            value = normalize_value(value, 4, 34)
        return value

    # SERIALIZATION
    @_machine.serializer()
    def save(self, state):
        return {"state": state}

    @_machine.unserializer()
    def _restore(self, blob):
        return blob["state"]

    @classmethod
    def from_blob(cls, blob, microcontroller, device, children=None):
        self = cls(microcontroller, device, children)
        self._restore(blob)
        return self

    # STATES
    @_machine.state(serialized="very_low")
    def very_low(self):
        pass

    @_machine.state(serialized="low")
    def low(self):
        pass

    @_machine.state(serialized="medium", initial=True)
    def medium(self):
        pass

    @_machine.state(serialized="high")
    def high(self):
        pass

    @_machine.state(serialized="very_high")
    def very_high(self):
        pass

    # OUTPUTS
    @_machine.output()
    def notify_user(self):
        blob = self.save()
        message = f'{self.device.name} is {blob["state"]}.'
        bot.send_message(chat_id=CHANNEL, text=message, parse_mode=telegram.ParseMode.HTML)
        return blob

    @_machine.output()
    def turn_off(self):
        for child in self.children:
            getattr(self, child.name).decrease()
        return False

    @_machine.output()
    def turn_on(self):
        for child in self.children:
            getattr(self, child.name).increase()
        return True


    # RULES (for changing the state and saving it)
    medium.upon(increase, enter=high, outputs=[save_state, turn_off], collector=itemgetter(0))
    medium.upon(decrease, enter=low, outputs=[save_state, turn_on], collector=itemgetter(0))

    high.upon(increase, enter=very_high, outputs=[save_state, notify_user], collector=itemgetter(0))
    high.upon(decrease, enter=medium, outputs=[save_state, turn_off], collector=itemgetter(0))
    low.upon(increase, enter=medium, outputs=[save_state, turn_off], collector=itemgetter(0))
    low.upon(decrease, enter=very_low, outputs=[save_state, notify_user], collector=itemgetter(0))

    very_low.upon(increase, enter=low, outputs=[save_state], collector=itemgetter(0))
    very_high.upon(decrease, enter=high, outputs=[save_state], collector=itemgetter(0))

    # avoid exception, make it invariant
    very_low.upon(decrease, enter=very_low, outputs=[report_state], collector=itemgetter(0))
    very_high.upon(increase, enter=very_high, outputs=[report_state], collector=itemgetter(0))

    # query value (read input, but the state remains)
    high.upon(query_value, enter=high, outputs=[read_value], collector=itemgetter(0))
    very_high.upon(query_value, enter=very_high, outputs=[read_value], collector=itemgetter(0))
    medium.upon(query_value, enter=medium, outputs=[read_value], collector=itemgetter(0))
    low.upon(query_value, enter=low, outputs=[read_value], collector=itemgetter(0))
    very_low.upon(query_value, enter=very_low, outputs=[read_value], collector=itemgetter(0))


class I2C:
    _machine = MethodicalMachine()

    def __init__(self, microcontroller, device, children=None):
        self.device = device
        self.microcontroller = microcontroller
        self.children = children if children is not None else []
        for child in self.children:
            setattr(self, child.name, child.get_fsm(microcontroller))

    # INPUTS
    @_machine.input()
    def query_value(self):
        pass

    @_machine.input()
    def increase(self):
        pass

    @_machine.input()
    def decrease(self):
        pass

    # OUTPUTS
    @_machine.output()
    def report_state(self):
        blob = self.save()
        return blob["state"]

    @_machine.output()
    def save_state(self):
        self.device.blob = self.save()
        self.device.save()
        return self.device.blob["state"]

    @_machine.output()
    def read_value(self):
        return self.device.read_data(self.microcontroller)

    # SERIALIZATION
    @_machine.serializer()
    def save(self, state):
        return {"state": state}

    @_machine.unserializer()
    def _restore(self, blob):
        return blob["state"]

    @classmethod
    def from_blob(cls, blob, microcontroller, device, children=None):
        self = cls(microcontroller, device, children)
        self._restore(blob)
        return self

    # STATES
    @_machine.state(serialized="very_low")
    def very_low(self):
        pass

    @_machine.state(serialized="low")
    def low(self):
        pass

    @_machine.state(serialized="medium", initial=True)
    def medium(self):
        pass

    @_machine.state(serialized="high")
    def high(self):
        pass

    @_machine.state(serialized="very_high")
    def very_high(self):
        pass

    # OUTPUTS
    @_machine.output()
    def notify_user(self):
        blob = self.save()
        message = f'{self.device.name} is {blob["state"]}.'
        bot.send_message(chat_id=CHANNEL, text=message, parse_mode=telegram.ParseMode.HTML)
        return blob

    @_machine.output()
    def turn_off(self):
        for child in self.children:
            getattr(self, child.name).decrease()
        return False

    @_machine.output()
    def turn_on(self):
        for child in self.children:
            getattr(self, child.name).increase()
        return True


    # RULES (for changing the state and saving it)
    medium.upon(increase, enter=high, outputs=[save_state], collector=itemgetter(0))
    medium.upon(decrease, enter=low, outputs=[save_state], collector=itemgetter(0))

    high.upon(increase, enter=very_high, outputs=[save_state, turn_on, notify_user], collector=itemgetter(0))
    high.upon(decrease, enter=medium, outputs=[save_state, turn_off], collector=itemgetter(0))
    low.upon(increase, enter=medium, outputs=[save_state], collector=itemgetter(0))
    low.upon(decrease, enter=very_low, outputs=[save_state, notify_user], collector=itemgetter(0))

    very_low.upon(increase, enter=low, outputs=[save_state], collector=itemgetter(0))
    very_high.upon(decrease, enter=high, outputs=[save_state], collector=itemgetter(0))

    # avoid exception, make it invariant
    very_low.upon(decrease, enter=very_low, outputs=[report_state], collector=itemgetter(0))
    very_high.upon(increase, enter=very_high, outputs=[report_state], collector=itemgetter(0))

    # query value (read input, but the state remains)
    high.upon(query_value, enter=high, outputs=[read_value], collector=itemgetter(0))
    very_high.upon(query_value, enter=very_high, outputs=[read_value], collector=itemgetter(0))
    medium.upon(query_value, enter=medium, outputs=[read_value], collector=itemgetter(0))
    low.upon(query_value, enter=low, outputs=[read_value], collector=itemgetter(0))
    very_low.upon(query_value, enter=very_low, outputs=[read_value], collector=itemgetter(0))


class PWM:
    _machine = MethodicalMachine()

    def __init__(self, microcontroller, device, children=None):
        self.device = device
        self.microcontroller = microcontroller
        self.children = children if children is not None else []
        for child in self.children:
            setattr(self, child.name, child.get_fsm(microcontroller))

    # INPUTS
    @_machine.input()
    def query_value(self):
        pass

    @_machine.input()
    def increase(self):
        pass

    @_machine.input()
    def decrease(self):
        pass

    # OUTPUTS
    @_machine.output()
    def report_state(self):
        blob = self.save()
        return blob["state"]

    @_machine.output()
    def save_state(self):
        self.device.blob = self.save()
        self.device.save()
        return self.device.blob["state"]

    @_machine.output()
    def read_value(self):
        return self.device.read_data(self.microcontroller)

    # SERIALIZATION
    @_machine.serializer()
    def save(self, state):
        return {"state": state}

    @_machine.unserializer()
    def _restore(self, blob):
        return blob["state"]

    @classmethod
    def from_blob(cls, blob, microcontroller, device, children=None):
        self = cls(microcontroller, device, children)
        self._restore(blob)
        return self

    # STATES
    @_machine.state(serialized="closed", initial=True)
    def closed(self):
        pass

    @_machine.state(serialized="opened")
    def opened(self):
        pass

    # OUTPUTS
    @_machine.output()
    def make_closed(self):
        return self.device.write_data(0, self.microcontroller)

    @_machine.output()
    def make_opened(self):
        return self.device.write_data(164, self.microcontroller)

    # RULES (for changing the state and saving it)
    closed.upon(increase, enter=opened, outputs=[save_state, make_opened], collector=itemgetter(0))
    opened.upon(decrease, enter=closed, outputs=[save_state, make_closed], collector=itemgetter(0))

    # avoid exception, make it invariant
    closed.upon(decrease, enter=closed, outputs=[report_state], collector=itemgetter(0))
    opened.upon(increase, enter=opened, outputs=[report_state], collector=itemgetter(0))

    # query value (read input, but the state remains)
    opened.upon(query_value, enter=opened, outputs=[read_value], collector=itemgetter(0))
    closed.upon(query_value, enter=closed, outputs=[read_value], collector=itemgetter(0))
