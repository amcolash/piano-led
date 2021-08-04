from enum import Enum, auto
import os
from pathlib import Path
import pickle
import pytz

import palettes

# File path of settings file
rootPath = str(Path(__file__).parent)
settingsFile = Path(rootPath + '/settings.p')

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

class Configuration:
  def __init__(self):
    ### Not restored on restart ###

    # Things that should be updated - note, these will be updated on the next cycle to avoid threading issues
    self.TO_UPDATE = {}
    self.DIRTY = False

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

    # Key Configuration
    self.MIN_KEY = 28
    self.MAX_KEY = 103
    self.TOTAL_KEYS = self.MAX_KEY - self.MIN_KEY

    ### Restored on restart ###

    # Playing Configuration
    self.FADE_SPEED = 5

    self.PLAY_MODE = PlayMode.BRIGHTEN_CURRENT

    # Scalar of how much to brighten colors with BRIGHTEN_CURRENT
    self.BRIGHTEN_AMOUNT = 10

    # Number of keys to ripple from
    self.RIPPLE_KEYS = 8

    # Color Configuration
    self.CURRENT_PALETTE = palettes.Palette.Ocean
    self.PALETTE = palettes.generatePalette(self.CURRENT_PALETTE.value, self.LED_COUNT)
    self.PALETTE_DIRTY = 0

    # Ambient Configuration
    self.NIGHT_MODE_ENABLED = True
    self.NIGHT_MODE_START_HOUR = 1 # Starting hour when night mode begins (inclusive)
    self.NIGHT_MODE_END_HOUR = 7 # Ending hour when night mode stops (exclusive)
    self.AMBIENT_MODE = AmbientMode.PALETTE_CYCLE
    self.AMBIENT_ENABLED = True

    self.CYCLE_SPEED = 0.15

  def updatePalette(self, pal):
    self.CURRENT_PALETTE = pal
    self.PALETTE = palettes.generatePalette(self.CURRENT_PALETTE.value, self.LED_COUNT)

    # Set this value to a counter so that we retry to set the value a few times, this is due to the button press triggering potentially
    # in the middle of the update cycle. We should technically only need 2 updates, but using 3 just in case. Plus, it adds a nice fade
    self.PALETTE_DIRTY = 3

    self.save()

  def updateValue(self, name, value):
    self.TO_UPDATE[name] = value
    if name == 'AMBIENT_MODE':
      self.TO_UPDATE['PALETTE_DIRTY'] = 3
    self.save()

  def load(self):
    if settingsFile.exists():
      loaded = pickle.load(open(settingsFile, "rb"))

      print(str(loaded.NIGHT_MODE_ENABLED))

      self.updatePalette(loaded.CURRENT_PALETTE)
      self.AMBIENT_ENABLED = loaded.AMBIENT_ENABLED
      self.AMBIENT_MODE = loaded.AMBIENT_MODE
      self.NIGHT_MODE_ENABLED = loaded.NIGHT_MODE_ENABLED
      self.PLAY_MODE = loaded.PLAY_MODE
      self.CYCLE_SPEED = loaded.CYCLE_SPEED

  def save(self):
    pickle.dump(self, open(settingsFile, "wb"))

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

      self.TO_UPDATE = {}

      # Save config after update
      self.save()

      # Tell Display that things are dirty for next update
      self.DIRTY = True

Config = Configuration()