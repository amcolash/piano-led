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
SPEED = 10

leds = []
for l in range(NUM_LEDS):
  leds.append({ 'current': [0,0,0], 'previous': [0,0,0], 'target1': [0,0,0], 'target2': [0,0,0], 'state': False, 'offCount': 0 })

colorIndex = 0

class MidiInputHandler(object):
  def __init__(self, port):
    self.port = port
    self._wallclock = time.time()

  def __call__(self, event, data=None):
    global colorIndex

    message, deltatime = event
    self._wallclock += deltatime
    # print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

    velocity = message[2]

    # Normal LED Order
    key = (message[1] - MIN_KEY)

    # Reverse LED Order
    # key = TOTAL_KEYS - (message[1] - MIN_KEY)

    led = int((key / (TOTAL_KEYS + 1)) * NUM_LEDS)

    if velocity > 0:
      leds[led]['state'] = True
      leds[led + 1]['state'] = True

      # newColor = wheel(colorIndex)
      newColor = hsv_to_rgb(colorIndex / 360, 1, 0.3)
      newColor[0] = int(newColor[0])
      newColor[1] = int(newColor[1])
      newColor[2] = int(newColor[2])

      # print(colorIndex)
      # print(newColor)

      leds[led]['target2'] = newColor
      leds[led + 1]['target2'] = newColor

      leds[led]['offCount'] = -1
      leds[led + 1]['offCount'] = -1

      # print(colorIndex)
      # print(wheel(colorIndex))

      colorIndex = (colorIndex + 10) % 360
    else:
      leds[led]['state'] = False
      leds[led + 1]['state'] = False

def hsv_to_rgb(h, s, v):
  if s == 0.0: v*=255; return [v, v, v]
  i = int(h*6.) # XXX assume int() truncates!
  f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
  if i == 0: return [v, t, p]
  if i == 1: return [q, v, p]
  if i == 2: return [p, v, t]
  if i == 3: return [p, q, v]
  if i == 4: return [t, p, v]
  if i == 5: return [v, p, q]

def updateLeds():
  try:
    for l in range(NUM_LEDS):
      led = leds[l]

      for c in range(3):
        led['previous'][c] = led['current'][c]

        dir = 0
        currentTarget = led['target2'] if led['state'] else led['target1']

        if abs(led['current'][c] - currentTarget[c]) <= SPEED: led['current'][c] = currentTarget[c]
        elif led['current'][c] < currentTarget[c]: led['current'][c] += SPEED
        elif led['current'][c] > currentTarget[c]: led['current'][c] -= SPEED

        # led['current'][c] = max(0, min(255, led['current'][c] + dir))

      if led['current'] != led['previous']:
        # print(led['current'])
        # print(led['previous'])
        bus.write_i2c_block_data(I2C_ADDRESS, l, led['current'])

      # Hacky bit of code to try and force LEDs off a few times after the final time they are pressed - in case a message gets missed so
      # they don't stay on forever
      if led['current'][0] + led['current'][1] + led['current'][2] == 0:
        if led['offCount'] == -1:
          led['offCount'] = 3
        elif led['offCount'] > 0:
          led['offCount'] -= 1
          bus.write_i2c_block_data(I2C_ADDRESS, l, led['target1'])

  except OSError:
    print(sys.exc_info()[0])

def wheel(pos):
  if pos < 85:
    return [pos * 3, 255 - pos * 3, 0]
  elif pos < 170:
    pos -= 85
    return [255 - pos * 3, 0, pos * 3]
  else:
    pos -= 170
    return [0, pos * 3, 255 - pos * 3]

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