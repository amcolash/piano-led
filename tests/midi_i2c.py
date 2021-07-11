import time

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
from smbus2 import SMBus

I2C_ADDRESS = 8
MIN_KEY = 28
MAX_KEY = 103
TOTAL_KEYS = MAX_KEY - MIN_KEY

NUM_LEDS = 144

color = [0,100,100]
off = [0,0,0]

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        # print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

        velocity = message[2]

        # Normal LED Order
        # key = (message[1] - MIN_KEY)

        # Reverse LED Order
        key = TOTAL_KEYS - (message[1] - MIN_KEY)

        led = int((key / (TOTAL_KEYS + 1)) * NUM_LEDS)

        if velocity > 0:
          bus.write_i2c_block_data(I2C_ADDRESS, led, color)
          bus.write_i2c_block_data(I2C_ADDRESS, led + 1, color)
        else:
          bus.write_i2c_block_data(I2C_ADDRESS, led, off)
          bus.write_i2c_block_data(I2C_ADDRESS, led + 1, off)

midiin, port_name = open_midiinput(1)
midiin.set_callback(MidiInputHandler(port_name))

bus = SMBus(1)

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin