from enum import Enum, auto
import jsonpickle
import os
from pathlib import Path
import pytz
import sys

from palettes import Palette, Palettes

# File path of settings file
rootPath = str(Path(__file__).parent)
settingsFile = Path(rootPath + '/settings.json')

savedValues = [
  'CURRENT_PALETTE',
  'AMBIENT_ENABLED',
  'AMBIENT_MODE',
  'NIGHT_MODE_ENABLED',
  'NIGHT_MODE_TIMEOUT',
  'PLAY_MODE',
  'CYCLE_SPEED',
  'DISPLAY_MENU_RESET',
  'DISPLAY_OFF_TIMEOUT',
  'MAX_AMBIENT_BRIGHTNESS',
  'MUSIC_PLAYING_OVERRIDE'
]

# PLAYING_MODE Options
class PlayMode(Enum):
  NONE = auto()
  CYCLE_COLORS = auto()
  BRIGHTEN_CURRENT = auto()
  RIPPLE = auto()

# AMBIENT_MODE Options
class AmbientMode(Enum):
  OFF = auto()
  SINGLE_COLOR = auto()
  BOUNCE = auto()
  PALETTE = auto()
  PALETTE_BREATH = auto()
  PALETTE_CYCLE = auto()
  PALETTE_CYCLE_SINGLE = auto()
  PALETTE_SCROLL = auto()

# Pending system action
class PendingAction(Enum):
  NONE = auto()
  SHUTDOWN = auto()
  REBOOT = auto()
  RESTART_SERVICE = auto()

class Configuration:
  def __init__(self):
    ### Not restored on restart ###

    # Things that should be updated - note, these will be updated on the next cycle to avoid threading issues
    self.TO_UPDATE = {}
    self.DIRTY = False
    self.SCROLL = None
    self.PENDING_ACTION = PendingAction.NONE

    # LED strip configuration:
    self.LED_COUNT = 148        # Number of LED pixels.
    self.LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
    self.LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    self.LED_DMA = 10          # DMA channel to use for generating signal (try 10)
    self.LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
    self.LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
    self.LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

    # Base Configuration
    self.I2C_BUS = 1
    self.I2C_MIDI_ADDRESS = 8
    self.I2C_DISPLAY_ADDRESS = 60
    self.DEBUG_MIDI = False
    self.DEBUG_I2C = False
    self.PROFILING = False
    self.FORWARD_MIDI = True
    self.MIDI_DEVICE = "Digital Keyboard" # A partial match of the midi device name
    self.TIMEZONE = pytz.timezone("America/Los_Angeles")
    self.PORT = 8080 # server port
    self.FPS = 100 # max updates per second. max updaes on pi2 currently peaks at 220. recommended to keep below to not fully use cpu

    # Key Configuration
    self.MIN_KEY = 28
    self.MAX_KEY = 103
    self.TOTAL_KEYS = self.MAX_KEY - self.MIN_KEY

    # Playing Configuration
    self.FADE_SPEED = 1

    # Timeout before menu goes back to main one (in minutes)
    self.DISPLAY_MENU_RESET = 2
    self.DISPLAY_OFF_TIMEOUT = 30
    self.DISPLAY_ON_FORCE = False # Toggles on display immediately

    self.PLAY_MODE = PlayMode.BRIGHTEN_CURRENT

    # Scalar of how much to brighten colors
    self.MAX_AMBIENT_BRIGHTNESS = 20
    self.BRIGHTEN_AMOUNT = 5

    # Number of keys to ripple from
    self.RIPPLE_KEYS = 3

    # Color Configuration
    self.CURRENT_PALETTE = Palette.Ocean
    self.PALETTE = Palettes.generatePalette(self.CURRENT_PALETTE.value, self.LED_COUNT)
    self.PALETTE_DIRTY = 0

    # Ambient Configuration
    self.AMBIENT_ENABLED = True
    self.AMBIENT_MODE = AmbientMode.PALETTE_CYCLE
    self.NIGHT_MODE_ENABLED = True
    self.NIGHT_MODE_TIMEOUT = 15
    self.NIGHT_MODE_START_HOUR = 0 # Starting hour when night mode begins (inclusive)
    self.NIGHT_MODE_START_MINUTE = 30 # Starting minute when night mode begins (inclusive)
    self.NIGHT_MODE_END_HOUR = 23 # Ending hour when night mode stops (exclusive)
    self.NIGHT_MODE_END_MINUTE = 30 # Ending minute when night mode stops (exclusive)
    self.MUSIC_PLAYING_OVERRIDE = True

    self.CYCLE_SPEED = 0.15

    self.CHORDS = False # Chord mode
    self.CHORDS_ENABLED = True # If current active
    self.CHORDS_MAJOR = True # Major or minor chords
    self.CHORDS_NOTES = "" # Notes to display

  def updatePalette(self, pal, save=True):
    self.CURRENT_PALETTE = pal
    self.PALETTE = Palettes.generatePalette(self.CURRENT_PALETTE.value, self.LED_COUNT)

    # Set this value to a counter so that we retry to set the value a few times, this is due to the button press triggering potentially
    # in the middle of the update cycle. We should technically only need 2 updates, but using 3 just in case. Plus, it adds a nice fade
    self.PALETTE_DIRTY = 3

    # Only save when we are intentionally changing this value
    if save: self.save()

  def updateValue(self, name, value):
    self.TO_UPDATE[name] = value
    if name == 'AMBIENT_MODE':
      self.TO_UPDATE['PALETTE_DIRTY'] = 3
    self.save()

  def load(self):
    try:
      if settingsFile.exists():
        f = open(settingsFile, "r")
        loaded = jsonpickle.decode(f.read())

        for s in savedValues:
          try:
            if s == 'CURRENT_PALETTE':
                found = getattr(Palette, loaded[s])
                self.updatePalette(found, False)
            elif s in loaded:
              setattr(self, s, loaded[s])

              if s == 'MAX_AMBIENT_BRIGHTNESS':
                Palettes.updateBrightness(loaded[s])

                # Regenerate palette based on new brightness
                self.updatePalette(self.CURRENT_PALETTE, False)
            else:
              print('Could not load saved value: ' + s)
          except:
            print('Failed to load setting: ' + s, sys.exc_info())

        # Just in case there is special logic used in the load, make sure we have latest
        self.save()
    except:
      print('Failed to parse settings file', sys.exc_info())

  def save(self):
    saved = {}
    for s in savedValues:
      if hasattr(self, s):
        if s == 'CURRENT_PALETTE':
          saved[s] = getattr(self, s).name
        else:
          saved[s] = getattr(self, s)
      else:
        print('Could not save unknown value: ' + s)

    # encode as json
    encoded = jsonpickle.encode(saved)
    with open(settingsFile, "w") as f:
      print(encoded, file=f)

  # This function is called every loop of the update to check if there are newly updated settings. Each is then modified and then after
  # all have been changed, the new config is saved. This prevents threading issues from the interrupt-based issues with button handlers.
  def update(self):
    keys = list(self.TO_UPDATE.keys())
    values = list(self.TO_UPDATE.values())

    if len(keys) > 0:
      for i in range(len(keys)):
        if keys[i] == 'CURRENT_PALETTE':
          self.updatePalette(values[i])
        else:
          setattr(self, keys[i], values[i])

          if keys[i] == 'MAX_AMBIENT_BRIGHTNESS':
            Palettes.updateBrightness(values[i])

            # Regenerate palette based on new brightness
            self.updatePalette(self.CURRENT_PALETTE, False)

      self.TO_UPDATE = {}

      # Save config after update
      self.save()

      # Tell Display that things are dirty for next update
      self.DIRTY = True

Config = Configuration()
