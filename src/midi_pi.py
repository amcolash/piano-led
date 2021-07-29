import cProfile
import datetime
import math
import pstats
import sys
import time

import rtmidi
from rpi_ws281x import PixelStrip, Color
from smbus2 import SMBus

from config import AmbientMode, Config, PlayMode
import palettes
import util

# Global Vars
lastPlayed = 0

palette = palettes.generatePalette(Config.CURRENT_PALETTE, Config.LED_COUNT)
cycle = 0

bus = None
midi_in_piano = rtmidi.MidiIn()
midi_in_system = rtmidi.MidiIn()
midi_out_piano = rtmidi.MidiOut()
midiCount = 0

leds = []
strip = PixelStrip(Config.LED_COUNT, Config.LED_PIN, Config.LED_FREQ_HZ, Config.LED_DMA, Config.LED_INVERT, Config.LED_BRIGHTNESS, Config.LED_CHANNEL)

# Begin Code

class MidiInputHandler(object):
  def __init__(self, port, piano):
    self.port = port
    self.wallclock = time.time()
    self.piano = piano
    self.colorIndex = 0

  def __call__(self, event, data=None):
    global colorIndex, lastPlayed, cycle, midi_out_piano

    message, deltatime = event
    self.wallclock += deltatime
    # print("[%s] @%0.6f %r" % (self.port, self.wallclock, message))

    # clamp velocity to make things a bit quieter
    if len(message) > 2: message[2] = min(80, message[2])

    # If we want to forward midi to piano and got an event
    if not self.piano and midi_out_piano.is_port_open():
      midi_out_piano.send_message(message)

    # Strip channel from message - all channels will be played
    event = message[0] >> 4

    # Only handle ON (0b1001) and OFF (0b1000) events on ANY channel
    if event == 0b1001 or event == 0b1000:
      velocity = message[2]
      is_on = event == 0b1001 and velocity > 0

      # print("[%s] @%0.6f %r %s" % (self.port, self.wallclock, message, is_on))

      # Forward piano midi messages to leonardo
      if self.piano:
        try:
          bus.write_i2c_block_data(Config.I2C_ADDRESS, 0, message)
        except:
          if Config.DEBUG_I2C: print(util.niceTime() + ': ' + str(sys.exc_info()))

      # Normal LED Order
      key = (message[1] - Config.MIN_KEY)

      led = int((key / (Config.TOTAL_KEYS + 1)) * Config.LED_COUNT)

      toUpdate = [led, led + 1]

      # Default to target2
      newColor = leds[led]['target2']

      # next color in cycle
      if Config.PLAYING_MODE == PlayMode.CYCLE_COLORS:
        newColor = palettes.hsv_to_rgb_int(self.colorIndex / 360, 1, 0.3)
        self.colorIndex = (self.colorIndex + 10) % 360

      # brighten current color (assume max ambient rgb of about 20)
      elif Config.PLAYING_MODE == PlayMode.BRIGHTEN_CURRENT:
        newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in leds[led]['target1']]

      elif Config.PLAYING_MODE == PlayMode.RIPPLE:
        # toUpdate = []
        leds[led]['ripple'] = is_on
        for i in range(led - Config.RIPPLE_KEYS, led + Config.RIPPLE_KEYS):
          if i >= 0 and i < Config.LED_COUNT and i not in toUpdate:
            toUpdate.append(i)

      lastPlayed = time.time()

      for i in toUpdate:
        if i >= 0 and i < Config.LED_COUNT:
          try:
            if is_on:
              leds[i]['state'].append(led)
            else:
              leds[i]['state'].remove(led)
          except:
            # print(util.niceTime() + ': ' + str(sys.exc_info()))
            x = 1

          if len(leds[i]['state']) == 0:
            leds[i]['ripple'] = False

          # print(str(i) + ', ' + str(leds[i]['state']))

          if Config.PLAYING_MODE == PlayMode.RIPPLE:
            if leds[i]['target1'] != [0,0,0]: newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in leds[i]['target1']]
            else: newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in palette[i]]

          leds[i]['target2'] = newColor
          leds[i]['playTime'] = lastPlayed

def updateLeds():
  global cycle
  try:
    start = time.time()
    ambient = time.time() - lastPlayed > 10
    hour = datetime.datetime.now(Config.TZ).hour

    if Config.AMBIENT_MODE == AmbientMode.BOUNCE or Config.AMBIENT_MODE == AmbientMode.PALETTE_BREATH:
      xpos = math.sin((cycle % Config.LED_COUNT) / Config.LED_COUNT * math.pi * 2) * Config.LED_COUNT
      b = (math.cos(cycle / 7) + 1) / 9 + 0.25
      b = 1
      c = palette[int(cycle)]
      breath = [int (b * c[0]), int (b * c[1]), int (b * c[2])]

    dirty = False

    for l in range(Config.LED_COUNT):
      led = leds[l]

      led['previous'][0] = led['current'][0]
      led['previous'][1] = led['current'][1]
      led['previous'][2] = led['current'][2]

      # time since last time played
      since = time.time() - led['playTime']

      # clear out LEDs when idle
      if since > 10 and len(led['state']) > 0: led['state'] = []

      # only update target1 when ambient mode is active - otherwise skip
      if ambient:
        # color
        if Config.AMBIENT_MODE == AmbientMode.SINGLE_COLOR:
          led['target1'] = Config.AMBIENT_COLOR

        # bounce
        elif Config.AMBIENT_MODE == AmbientMode.BOUNCE:
          if abs(l - xpos) < 5: led['target1'] = palette[int(cycle / 10 % Config.LED_COUNT)]
          else: led['target1'] = [0,0,0]

        # palette
        elif Config.AMBIENT_MODE == AmbientMode.PALETTE:
          led['target1'] = palette[l]

        # palette cycle
        elif Config.AMBIENT_MODE == AmbientMode.PALETTE_CYCLE:
          led['target1'] = palette[int((Config.LED_COUNT - l + cycle * 2)) % Config.LED_COUNT]

        # palette cycle single color
        elif Config.AMBIENT_MODE == AmbientMode.PALETTE_CYCLE_SINGLE:
          led['target1'] = palette[int(cycle) % Config.LED_COUNT]

        # scroll palette
        elif Config.AMBIENT_MODE == AmbientMode.PALETTE_SCROLL:
          seg = math.cos(((Config.LED_COUNT - l + cycle) / Config.LED_COUNT) * 3 * math.pi)
          if abs(seg) > 0.95: led['target1'] = palette[int(cycle / 2 % Config.LED_COUNT)]
          else: led['target1'] = [0, 0, 0]

        elif Config.AMBIENT_MODE == AmbientMode.PALETTE_BREATH:
          led['target1'] = breath

      # Ripple
      if not ambient and Config.PLAYING_MODE == PlayMode.RIPPLE and l in led['state']:
        # print(l)
        pos = int(abs(math.sin(since * 10)) * Config.RIPPLE_KEYS)
        toUpdate = [l + pos, l - pos]
        for u in toUpdate:
          # print(toUpdate)
          if u >= 0 and u < Config.LED_COUNT:
            leds[u]['ripple'] = True

      if Config.PLAYING_MODE == PlayMode.RIPPLE:
        currentTarget = led['target2'] if led['ripple'] else led['target1']
      else:
        currentTarget = led['target2'] if len(led['state']) > 0 else led['target1']

      # keep LEDs off at night
      if Config.NIGHT_MODE_ENABLED and hour >= Config.NIGHT_MODE_START_HOUR and hour < Config.NIGHT_MODE_END_HOUR and ambient:
        currentTarget = [0,0,0]

      if led['current'] == currentTarget:
        continue

      for c in range(3):
        if abs(led['current'][c] - currentTarget[c]) <= Config.FADE_SPEED: led['current'][c] = currentTarget[c]
        elif led['current'][c] < currentTarget[c]: led['current'][c] = min(currentTarget[c], int((led['current'][c] + 1) * 1.25))
        elif led['current'][c] > currentTarget[c]: led['current'][c] = max(currentTarget[c], int((led['current'][c] + 1) * 0.75))
        # elif led['current'][c] < currentTarget[c]: led['current'][c] += Config.FADE_SPEED
        # elif led['current'][c] > currentTarget[c]: led['current'][c] -= Config.FADE_SPEED

      # led['current'] = palettes.lerpColor(led['current'], currentTarget, 0.2)

      if led['current'] != led['previous']:
        strip.setPixelColor(l, Color(int(led['current'][0]), int(led['current'][1]), int(led['current'][2])))
        dirty = True

    if dirty:
      strip.show()

    # util.logTime(start, 'updateLeds')
    if ambient: cycle += Config.CYCLE_SPEED
    if cycle > Config.LED_COUNT:
      cycle -= Config.LED_COUNT

  except OSError:
    print(util.niceTime() + ': ' + sys.exc_info())

def initI2C():
  global bus
  bus = SMBus(1)

def initMidi():
  global midi_in_system, midi_in_piano, midi_out_piano, midiCount

  try:
    midiCount = 100

    if not midi_in_system.is_port_open():
      port_name = midi_in_system.open_port(0)
      midi_in_system.set_callback(MidiInputHandler(port_name, False))
      midi_in_system.set_client_name('System MIDI In')

    ports = midi_in_piano.get_ports()
    keyboard_present = any(Config.MIDI_DEVICE in string for string in ports)

    if not keyboard_present:
      if midi_in_piano.is_port_open():
        if Config.DEBUG_MIDI: print('Closing old port')
        midi_in_piano.close_port()
        midi_out_piano.close_port()
      else:
        if Config.DEBUG_MIDI: print('No Device')
    else:
      if not midi_in_piano.is_port_open():
        if Config.DEBUG_MIDI: print('Init MIDI')
        port_name = midi_in_piano.open_port(1)
        midi_in_piano.set_callback(MidiInputHandler(port_name, True))
        midi_in_piano.set_client_name('Piano MIDI In')

        midi_out_piano.open_port(1)
        midi_out_piano.set_client_name('Piano MIDI Out')
      else:
        if Config.DEBUG_MIDI: print('MIDI Fine')
  except:
    print(sys.exc_info())

def initLeds():
  global leds, strip
  for l in range(Config.LED_COUNT):
    leds.append({ 'current': [-1,-1,-1], 'previous': [0,0,0], 'target1': [0,0,0], 'target2': [0,0,0], 'state': [], 'playTime': 0, 'ripple': False })
  strip.begin()

try:
  print(util.niceTime() + ': Entering main loop. Press Control-C to exit.')

  initI2C()
  initLeds()

  # Just wait for keyboard interrupt,
  # everything else is handled via the input callback.
  while True:
    if midiCount == 0:
      initMidi()
    midiCount -= 1

    if Config.PROFILING:
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
    midi_in_piano.close_port()
    midi_out_piano.close_port()
    midi_in_system.close_port()
    del midi_in_piano
    del midi_out_piano
    del midi_in_system