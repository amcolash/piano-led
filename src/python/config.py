from enum import Enum, auto
import pytz

import palettes

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

class Config:
  # LED strip configuration:
  LED_COUNT = 148        # Number of LED pixels.
  LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
  LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
  LED_DMA = 10          # DMA channel to use for generating signal (try 10)
  LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
  LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
  LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

  # Base Configuration
  I2C_BUS = 1
  I2C_ADDRESS = 8
  DEBUG_MIDI = False
  DEBUG_I2C = False
  PROFILING = False
  FORWARD_MIDI = True
  MIDI_DEVICE = "Digital Keyboard" # A partial match of the midi device name
  TIMEZONE = pytz.timezone("America/Los_Angeles")

  # Key Configuration
  MIN_KEY = 28
  MAX_KEY = 103
  TOTAL_KEYS = MAX_KEY - MIN_KEY

  # Playing Configuration
  FADE_SPEED = 5

  PLAYING_MODE = PlayMode.BRIGHTEN_CURRENT

  # Scalar of how much to brighten colors with BRIGHTEN_CURRENT
  BRIGHTEN_AMOUNT = 10

  # Number of keys to ripple from
  RIPPLE_KEYS = 4

  # Color Configuration
  CURRENT_PALETTE = palettes.Ocean
  PALETTE = palettes.generatePalette(CURRENT_PALETTE, LED_COUNT)

  # Ambient Configuration
  NIGHT_MODE_ENABLED = True
  NIGHT_MODE_START_HOUR = 1 # Starting hour when night mode begins (inclusive)
  NIGHT_MODE_END_HOUR = 7 # Ending hour when night mode stops (exclusive)
  AMBIENT_MODE = AmbientMode.PALETTE

  # Color for single color mode
  AMBIENT_COLOR = [0,20,0]

  CYCLE_SPEED = 0.15