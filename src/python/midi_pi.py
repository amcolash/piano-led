import cProfile
import pstats

from config import Config
from display import Display
from i2c import I2C
from leds import Leds
from midi_ports import MidiPorts
import util

try:
  print(util.niceTime() + ': Entering main loop. Press Control-C to exit.')

  Leds.init()
  I2C.init()

  disp = Display()

  # Just wait for keyboard interrupt, everything else is handled via the input callback.
  while True:
    MidiPorts.update()

    if Config.PROFILING:
      profile = cProfile.Profile()
      profile.enable()

      i = 0
      while i < 500:
        Leds.updateLeds()
        i += 1

      profile.disable()
      ps = pstats.Stats(profile)
      ps.print_stats()

      break

    Leds.updateLeds()
    disp.update()

    # time.sleep(0.0005)
except KeyboardInterrupt:
  print('')
finally:
  MidiPorts.cleanup()
  print('Exit')