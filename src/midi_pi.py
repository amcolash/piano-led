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
from leds import Leds
import palettes
import util

# Global Vars
bus = None
midi_in_piano = rtmidi.MidiIn()
midi_in_system = rtmidi.MidiIn()
midi_out_piano = rtmidi.MidiOut()
midiCount = 0

leds = Leds()

# Begin Code

class MidiInputHandler(object):
  def __init__(self, port, piano):
    self.port = port
    self.wallclock = time.time()
    self.piano = piano
    self.colorIndex = 0

  def __call__(self, event, data=None):
    global midi_out_piano

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
      mainLed = leds.leds[led]
      newColor = mainLed['target2']

      # next color in cycle
      if Config.PLAYING_MODE == PlayMode.CYCLE_COLORS:
        newColor = palettes.hsv_to_rgb_int(self.colorIndex / 360, 1, 0.3)
        self.colorIndex = (self.colorIndex + 10) % 360

      # brighten current color (assume max ambient rgb of about 20)
      elif Config.PLAYING_MODE == PlayMode.BRIGHTEN_CURRENT:
        newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in mainLed['target1']]

      elif Config.PLAYING_MODE == PlayMode.RIPPLE:
        # toUpdate = []
        mainLed['ripple'] = is_on
        for i in range(led - Config.RIPPLE_KEYS, led + Config.RIPPLE_KEYS):
          if i >= 0 and i < Config.LED_COUNT and i not in toUpdate:
            toUpdate.append(i)

      leds.lastPlayed = time.time()

      for i in toUpdate:
        if i >= 0 and i < Config.LED_COUNT:
          updateLed = leds.leds[i]

          try:
            if is_on:
              updateLed['state'].append(led)
            else:
              updateLed['state'].remove(led)
          except:
            # print(util.niceTime() + ': ' + str(sys.exc_info()))
            x = 1

          if len(updateLed['state']) == 0:
            updateLed['ripple'] = False

          # print(str(i) + ', ' + str(updateLed['state']))

          if Config.PLAYING_MODE == PlayMode.RIPPLE:
            if updateLed['target1'] != [0,0,0]: newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in updateLed['target1']]
            else: newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in Config.PALETTE[i]]

          updateLed['target2'] = newColor
          updateLed['playTime'] = leds.lastPlayed

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

try:
  print(util.niceTime() + ': Entering main loop. Press Control-C to exit.')

  initI2C()

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
        leds.updateLeds()
        i += 1

      profile.disable()
      ps = pstats.Stats(profile)
      ps.print_stats()

      break

    leds.updateLeds()
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