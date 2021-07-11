import sys
import time

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
from smbus2 import SMBus

I2C_ADDRESS = 8
MIN_KEY = 28
MAX_KEY = 103
TOTAL_KEYS = MAX_KEY - MIN_KEY

NUM_LEDS = 144
SPEED = 70

leds = []
for l in range(NUM_LEDS):
  leds.append({ 'current': [0,0,0], 'previous': [0,0,0], 'target1': [0,0,0], 'target2': [0,100,100], 'state': False })

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
          leds[led]['state'] = True
          leds[led + 1]['state'] = True
        else:
          leds[led]['state'] = False
          leds[led + 1]['state'] = False

def updateLeds():
  try:
    for l in range(NUM_LEDS):
      led = leds[l]

      for c in range(2):
        led['previous'][c] = led['current'][c]

        dir = 0
        if led['state'] and led['current'][c] < led['target2'][c]: dir = 10
        if not led['state'] and led['current'][c] > led['target1'][c]: dir = -10

        led['current'][c] = max(0, min(255, led['current'][c] + dir))

      if led['current'] != led['previous']:
        # print(led['current'])
          bus.write_i2c_block_data(I2C_ADDRESS, l, led['current'])
  except OSError:
    print(sys.exc_info()[0])

midiin, port_name = open_midiinput(1)
midiin.set_callback(MidiInputHandler(port_name))

bus = SMBus(1)

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
      updateLeds()
      time.sleep(0.005)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin