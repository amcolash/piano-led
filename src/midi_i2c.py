import math
import sys
import time

import rtmidi
from smbus2 import SMBus

DEBUG_MIDI = False

I2C_ADDRESS = 8
MIN_KEY = 28
MAX_KEY = 103
TOTAL_KEYS = MAX_KEY - MIN_KEY

NUM_LEDS = 144
FADE_SPEED = 10

lastPlayed = 0

class MidiInputHandler(object):
  def __init__(self, port):
    self.port = port
    self._wallclock = time.time()

  def __call__(self, event, data=None):
    global colorIndex, lastPlayed

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

      newColor = hsv_to_rgb_int(colorIndex / 360, 1, 0.3)

      leds[led]['target2'] = newColor
      leds[led + 1]['target2'] = newColor

      leds[led]['offCount'] = -1
      leds[led + 1]['offCount'] = -1

      colorIndex = (colorIndex + 10) % 360

      lastPlayed = time.time()
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

def hsv_to_rgb_int(h, s, v):
  rgb = hsv_to_rgb(h, s, v)
  return [int(rgb[0]), int(rgb[1]), int(rgb[2])]

wheel_bright = []
wheel_dim = []
for l in range(NUM_LEDS):
  wheel_bright.append(hsv_to_rgb_int(l / NUM_LEDS, 1, 0.2))
  wheel_dim.append(hsv_to_rgb_int(l / NUM_LEDS, 1, 0.015))

cycle = 0
def updateLeds():
  global cycle
  try:
    p = 0
    packet = []

    ambient = time.time() - lastPlayed > 10
    wheel = wheel_bright if ambient else wheel_dim
    wheel = wheel_dim

    # ambient = 0.015

    xpos = math.sin((cycle % NUM_LEDS) / NUM_LEDS * math.pi) * NUM_LEDS

    for l in range(NUM_LEDS):
      led = leds[l]

      # color
      led['target1'] = [0,0,0]

      # bounce
      # if abs(l - xpos) < 5: led['target1'] = wheel[int(cycle / 10 % NUM_LEDS)]
      # else: led['target1'] = [0,0,0]

      # rainbow
      # led['target1'] = wheel[int((NUM_LEDS - l + cycle * 0.15) % NUM_LEDS)]

      # cycle
      # led['target1'] = wheel[int(cycle % NUM_LEDS)]

      # scroll rainbow
      # seg = math.cos(((NUM_LEDS - l + cycle) / NUM_LEDS) * 3 * math.pi)
      # if abs(seg) > 0.95: led['target1'] = wheel[int(cycle / 2 % NUM_LEDS)]
      # else: led['target1'] = [0, 0, 0]

      for c in range(3):
        led['previous'][c] = led['current'][c]

        dir = 0
        currentTarget = led['target2'] if led['state'] else led['target1']

        if abs(led['current'][c] - currentTarget[c]) <= FADE_SPEED: led['current'][c] = currentTarget[c]
        elif led['current'][c] < currentTarget[c]: led['current'][c] += FADE_SPEED
        elif led['current'][c] > currentTarget[c]: led['current'][c] -= FADE_SPEED

      if led['current'] != led['previous']:
        packet.append(l)
        packet.extend(led['current'])

      # TODO: Send LED data to over usb serial instead of i2c for speed?

      # Hacky bit of code to try and force LEDs off a few times after the final time they are pressed - in case a message gets missed so
      # they don't stay on forever
      # elif led['current'][0] == led['target1'][0] and led['current'][1] == led['target1'][1] and led['current'][2] == led['target1'][2]:
      #   if led['offCount'] == -1:
      #     led['offCount'] = 3
      #   elif led['offCount'] > 0:
      #     led['offCount'] -= 1

      #     packet.append(l)
      #     packet.extend(led['current'])

      if len(packet) == 4 * 7:
        bus.write_i2c_block_data(I2C_ADDRESS, 0, packet)
        packet = []

    if len(packet) > 0:
      bus.write_i2c_block_data(I2C_ADDRESS, 0, packet)

    if ambient: cycle += 0.15

  except OSError:
    print(sys.exc_info())

bus = None
midi_in = rtmidi.MidiIn()
midiCount = 0

midi_out = rtmidi.MidiOut()
for port_name in midi_out.get_ports():
    print(port_name)

def initMidi():
  global midi_in, midiCount

  try:
    midiCount = 100

    if midi_in.get_port_count() < 2:
      if midi_in.is_port_open():
        if DEBUG_MIDI: print('Closing old port')
        midi_in.close_port()
      else:
        if DEBUG_MIDI: print('No Device')
    else:
      if not midi_in.is_port_open():
        if DEBUG_MIDI: print('Init MIDI')
        port_name = midi_in.open_port(1)
        midi_in.set_callback(MidiInputHandler(port_name))
      else:
        if DEBUG_MIDI: print('MIDI Fine')
  except:
    print(sys.exc_info())

def initI2C():
  global bus
  bus = SMBus(1)

leds = []
colorIndex = 0

def initLeds():
  global leds
  for l in range(NUM_LEDS):
    leds.append({ 'current': [-1,-1,-1], 'previous': [-1,-1,-1], 'target1': [0,0,0], 'target2': [0,0,0], 'state': False, 'offCount': 0 })


print("Entering main loop. Press Control-C to exit.")
try:
  initI2C()
  initLeds()

  # Just wait for keyboard interrupt,
  # everything else is handled via the input callback.
  while True:
    if midiCount == 0:
      initMidi()
    midiCount -= 1

    updateLeds()
    time.sleep(0.005)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midi_in.close_port()
    del midi_in