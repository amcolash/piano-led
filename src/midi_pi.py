import cProfile
import datetime
from enum import Enum, auto
import math
import pstats
import pytz
import sys
import time

import rtmidi
from rpi_ws281x import PixelStrip, Color
from smbus2 import SMBus

import palettes

# LED strip configuration:
LED_COUNT = 148        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Base Configuration
I2C_ADDRESS = 8
DEBUG_MIDI = False
PROFILING = False

# Key Configuration
MIN_KEY = 28
MAX_KEY = 103
TOTAL_KEYS = MAX_KEY - MIN_KEY

# Playing Configuration
FADE_SPEED = 5

# PLAYING_MODE Options
class PlayMode(Enum):
  NONE = auto()
  CYCLE_COLORS = auto()
  BRIGHTEN_CURRENT = auto()

PLAYING_MODE = PlayMode.BRIGHTEN_CURRENT

# Color Configuration
CURRENT_PALETTE = palettes.Pink

# Ambient Configuration
NIGHT_MODE_ENABLED = True
NIGHT_MODE_START_HOUR = 1 # Starting hour when night mode begins (inclusive)
NIGHT_MODE_END_HOUR = 7 # Ending hour when night mode stops (exclusive)

# AMBIENT_MODE Options
class AmbientMode(Enum):
  OFF = auto()
  SINGLE_COLOR = auto()
  BOUNCE = auto()
  PALETTE = auto()
  PALETTE_CYCLE = auto()
  PALETTE_CYCLE_SINGLE = auto()
  PALETTE_SCROLL = auto()

AMBIENT_MODE = AmbientMode.OFF

# Color for single color mode
AMBIENT_COLOR = [0,20,0]

CYCLE_SPEED = 0.15

# Global Vars
lastPlayed = 0

palette = palettes.generatePalette(CURRENT_PALETTE, LED_COUNT)
cycle = 0
colorIndex = 0

bus = None
midi_in = rtmidi.MidiIn()
midiCount = 0

leds = []
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

tz = pytz.timezone('America/Los_Angeles')

# Begin Code

class MidiInputHandler(object):
  def __init__(self, port):
    self.port = port
    self._wallclock = time.time()

  def __call__(self, event, data=None):
    global colorIndex, lastPlayed, cycle

    message, deltatime = event
    self._wallclock += deltatime
    # print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

    # Forward midi message to leonardo
    try:
      bus.write_i2c_block_data(I2C_ADDRESS, 0, message)
    except:
      print(str(time.time()) + ': ' + str(sys.exc_info()))

    velocity = message[2]

    # Normal LED Order
    key = (message[1] - MIN_KEY)

    led = int((key / (TOTAL_KEYS + 1)) * LED_COUNT)

    if velocity > 0:
      leds[led]['state'] = True
      leds[led + 1]['state'] = True

      # do nothing
      if PLAYING_MODE == PlayMode.NONE:
        newColor = leds[led]['target2']

      # next color in cycle
      elif PLAYING_MODE == PlayMode.CYCLE_COLORS:
        newColor = hsv_to_rgb_int(colorIndex / 360, 1, 0.3)
        colorIndex = (colorIndex + 10) % 360

      # brighten current color (assume max ambient rgb of about 20)
      elif PLAYING_MODE == PlayMode.BRIGHTEN_CURRENT:
        newColor = [min(255, c * 10) for c in leds[led]['target1']]

      leds[led]['target2'] = newColor
      leds[led + 1]['target2'] = newColor

      leds[led]['offCount'] = -1
      leds[led + 1]['offCount'] = -1

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

def updateLeds():
  global cycle
  try:
    start = time.time()
    ambient = time.time() - lastPlayed > 10
    hour = datetime.datetime.now(tz).hour

    if AMBIENT_MODE == AmbientMode.BOUNCE:
      xpos = math.sin((cycle % LED_COUNT) / LED_COUNT * math.pi) * LED_COUNT

    dirty = False

    for l in range(LED_COUNT):
      led = leds[l]

      led['previous'][0] = led['current'][0]
      led['previous'][1] = led['current'][1]
      led['previous'][2] = led['current'][2]

      # off
      if AMBIENT_MODE == AmbientMode.OFF:
        led['target1'] = [0,0,0]

      # color
      elif AMBIENT_MODE == AmbientMode.SINGLE_COLOR:
        led['target1'] = AMBIENT_COLOR

      # bounce
      elif AMBIENT_MODE == AmbientMode.BOUNCE:
        if abs(l - xpos) < 5: led['target1'] = palette[int(cycle / 10 % LED_COUNT)]
        else: led['target1'] = [0,0,0]

      # palette
      elif AMBIENT_MODE == AmbientMode.PALETTE:
        led['target1'] = palette[l]

      # palette cycle
      elif AMBIENT_MODE == AmbientMode.PALETTE_CYCLE:
        led['target1'] = palette[int((LED_COUNT - l + cycle * 2)) % LED_COUNT]

      # palette cycle single color
      elif AMBIENT_MODE == AmbientMode.PALETTE_CYCLE_SINGLE:
        led['target1'] = palette[int(cycle) % LED_COUNT]

      # scroll palette
      elif AMBIENT_MODE == AmbientMode.PALETTE_SCROLL:
        seg = math.cos(((LED_COUNT - l + cycle) / LED_COUNT) * 3 * math.pi)
        if abs(seg) > 0.95: led['target1'] = palette[int(cycle / 2 % LED_COUNT)]
        else: led['target1'] = [0, 0, 0]

      # keep LEDs off at night
      if NIGHT_MODE_ENABLED and hour >= NIGHT_MODE_START_HOUR and hour < NIGHT_MODE_END_HOUR and ambient:
        led['target1'] = [0,0,0]

      currentTarget = led['target2'] if led['state'] else led['target1']
      if led['current'] == currentTarget:
        continue

      for c in range(3):
        if abs(led['current'][c] - currentTarget[c]) <= FADE_SPEED: led['current'][c] = currentTarget[c]
        elif led['current'][c] < currentTarget[c]: led['current'][c] += FADE_SPEED
        elif led['current'][c] > currentTarget[c]: led['current'][c] -= FADE_SPEED

      # led['current'] = palettes.lerpColor(led['current'], currentTarget, 0.1)

      if led['current'] != led['previous']:
        strip.setPixelColor(l, Color(led['current'][0], led['current'][1], led['current'][2]))
        dirty = True

    if dirty:
      strip.show()

    # logTime(start, 'updateLeds')
    if ambient: cycle += CYCLE_SPEED
    if cycle > LED_COUNT:
      cycle -= LED_COUNT

  except OSError:
    print(sys.exc_info())

def logTime(start, label):
  print(label + ': ' + str((time.time() - start) * 1000))

def initI2C():
  global bus
  bus = SMBus(1)

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

def initLeds():
  global leds, strip
  for l in range(LED_COUNT):
    leds.append({ 'current': [-1,-1,-1], 'previous': [0,0,0], 'target1': [0,0,0], 'target2': [0,0,0], 'state': False, 'offCount': 0 })
  strip.begin()

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

    if PROFILING:
      profile = cProfile.Profile()
      profile.enable()

      i = 0
      while i < 500:
        updateLeds()
        i += 1

      profile.disable()
      ps = pstats.Stats(profile)
      ps.print_stats()

      break

    updateLeds()
    # time.sleep(0.0005)
except KeyboardInterrupt:
    print('')
finally:
    print('Exit')
    midi_in.close_port()
    del midi_in