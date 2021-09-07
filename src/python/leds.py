import datetime
import math
from rpi_ws281x import PixelStrip, Color
import time

from config import AmbientMode, Config, PlayMode
import util

# Make a lookup cache of every color to try to have better performance
CACHED_COLORS = {}

# This class is a singleton

class Leds:
  strip = None
  leds = []
  cycle = 0
  lastPlayed = 0

  @classmethod
  def init(cls):
    cls.strip = PixelStrip(Config.LED_COUNT, Config.LED_PIN, Config.LED_FREQ_HZ, Config.LED_DMA, Config.LED_INVERT, Config.LED_BRIGHTNESS, Config.LED_CHANNEL)
    cls.strip.begin()

    for l in range(Config.LED_COUNT):
      cls.leds.append({ 'current': [-1,-1,-1], 'previous': [0,0,0], 'target1': [0,0,0], 'target2': [0,0,0], 'state': [], 'playTime': 0, 'ripple': False })

  @classmethod
  def clearLeds(cls):
    if len(cls.leds) == Config.LED_COUNT:
      for l in range(Config.LED_COUNT):
        cls.leds[l]['state'] = []

  @classmethod
  def updateLeds(cls):
    try:
      start = time.time()
      ambient = time.time() - cls.lastPlayed > Config.NIGHT_MODE_TIMEOUT
      hour = datetime.datetime.now(Config.TIMEZONE).hour

      if Config.AMBIENT_MODE == AmbientMode.BOUNCE or Config.AMBIENT_MODE == AmbientMode.PALETTE_BREATH:
        xpos = math.sin((cls.cycle % Config.LED_COUNT) / Config.LED_COUNT * math.pi * 2) * Config.LED_COUNT
        b = (math.cos(cls.cycle / 7) + 1) / 9 + 0.25
        b = 1
        c = Config.PALETTE[int(cls.cycle)]
        breath = [int (b * c[0]), int (b * c[1]), int (b * c[2])]

      dirty = False

      for l in range(Config.LED_COUNT):
        led = cls.leds[l]

        led['previous'][0] = led['current'][0]
        led['previous'][1] = led['current'][1]
        led['previous'][2] = led['current'][2]

        # time since last time played
        since = time.time() - led['playTime']

        # clear out LEDs when idle
        if since > 10 and len(led['state']) > 0: led['state'] = []
        if Config.PALETTE_DIRTY == 1: led['state'] = []

        # only update target1 when ambient mode is active - otherwise skip
        if ambient or Config.PALETTE_DIRTY > 0:
          # color
          if Config.AMBIENT_MODE == AmbientMode.SINGLE_COLOR:
            led['target1'] = Config.PALETTE[0]

          # bounce
          elif Config.AMBIENT_MODE == AmbientMode.BOUNCE:
            if abs(l - xpos) < 5: led['target1'] = Config.PALETTE[int(cls.cycle / 10 % Config.LED_COUNT)]
            else: led['target1'] = [0,0,0]

          # palette
          elif Config.AMBIENT_MODE == AmbientMode.PALETTE:
            led['target1'] = Config.PALETTE[l]

          # palette cycle
          elif Config.AMBIENT_MODE == AmbientMode.PALETTE_CYCLE:
            led['target1'] = Config.PALETTE[int((Config.LED_COUNT - l + cls.cycle * 2)) % Config.LED_COUNT]

          # palette cycle single color
          elif Config.AMBIENT_MODE == AmbientMode.PALETTE_CYCLE_SINGLE:
            led['target1'] = Config.PALETTE[int(cls.cycle) % Config.LED_COUNT]

          # scroll palette
          elif Config.AMBIENT_MODE == AmbientMode.PALETTE_SCROLL:
            seg = math.cos(((Config.LED_COUNT - l + cls.cycle) / Config.LED_COUNT) * 3 * math.pi)
            if abs(seg) > 0.95: led['target1'] = Config.PALETTE[int(cls.cycle / 2 % Config.LED_COUNT)]
            else: led['target1'] = [0, 0, 0]

          elif Config.AMBIENT_MODE == AmbientMode.PALETTE_BREATH:
            led['target1'] = breath

        # Ripple
        if not ambient and Config.PLAY_MODE == PlayMode.RIPPLE and l in led['state']:
          # print(l)
          pos = int(abs(math.sin(since * 10)) * Config.RIPPLE_KEYS)
          toUpdate = [l + pos, l - pos]
          for u in toUpdate:
            # print(toUpdate)
            if u >= 0 and u < Config.LED_COUNT:
              cls.leds[u]['ripple'] = True

        ambientColor = led['target1'] if Config.AMBIENT_ENABLED else [0, 0, 0]

        if Config.PLAY_MODE == PlayMode.RIPPLE:
          currentTarget = led['target2'] if led['ripple'] else ambientColor
        else:
          currentTarget = led['target2'] if len(led['state']) > 0 else ambientColor

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

        # led['current'] = Palettes.lerpColor(led['current'], currentTarget, 0.2)

        if led['current'] != led['previous']:
          vals = int(led['current'][0]), int(led['current'][1]), int(led['current'][2])
          rgb_lookup = str(vals[0]) + str(vals[1]) + str(vals[2])

          # Doesn't look like this helps at all :(
          if rgb_lookup in CACHED_COLORS:
            color = CACHED_COLORS[rgb_lookup]
          else:
            color = Color(vals[0], vals[1], vals[2])
            CACHED_COLORS[rgb_lookup] = color

          cls.strip.setPixelColor(l, color)
          dirty = True


      if Config.PALETTE_DIRTY > 0:
        Config.PALETTE_DIRTY -= 1

      if dirty:
        cls.strip.show()

      # util.logTime(start, 'updateLeds')
      if ambient: cls.cycle += Config.CYCLE_SPEED
      if cls.cycle > Config.LED_COUNT:
        cls.cycle -= Config.LED_COUNT

    except OSError:
      print(util.niceTime() + ': ' + sys.exc_info())