import cProfile
import pstats
import time

from config import Config
from display import Display
from i2c import I2C
from leds import Leds
from midi_ports import MidiPorts
from music import Music
import util

class MidiPi:
  def __init__(self):
    Config.load()
    Leds.init()
    I2C.init()
    self.Disp = Display()

  def update(self):
    MidiPorts.update()
    Config.update()
    Leds.updateLeds()
    Music.update()
    self.Disp.update()

  def profile(self):
    # Just wait for keyboard interrupt, everything else is handled via the input callback.
    profile = cProfile.Profile()
    profile.enable()

    i = 0
    while i < 500:
      self.update()
      i += 1

    profile.disable()
    ps = pstats.Stats(profile)
    ps.print_stats()

try:
  print(util.niceTime() + ': Entering main loop. Press Control-C to exit.')

  midiPi = MidiPi()

  while True:
    if Config.PROFILING:
      midiPi.profile()
      break

    midiPi.update()
    # time.sleep(0.0005)
finally:
  MidiPorts.cleanup()
  print('Exit')