import cProfile
import pstats
import sys
import time
from threading import Thread

from config import Config
from display import Display
from i2c import I2C
from leds import Leds
from midi_ports import MidiPorts
from music import Music
from power import Power
from server import Server
from util import niceTime, updatePendingActions

class MidiPi:
  def __init__(self):
    Config.load()
    Music.init()
    Leds.init()
    I2C.init()
    Power.init()
    self.Display = Display()

    self.serverThread = Thread(target=Server.init)
    self.serverThread.daemon = True
    self.serverThread.start()

    print('Init Complete')

  def update(self):
    MidiPorts.update()
    Config.update()
    Leds.updateLeds()
    Music.update()
    self.Display.update()
    updatePendingActions(self.Display)

  def profile(self):
    # Just wait for keyboard interrupt, everything else is handled via the input callback.
    profile = cProfile.Profile()
    profile.enable()

    i = 0
    while i < 300:
      self.update()
      i += 1

    profile.disable()
    ps = pstats.Stats(profile)
    ps.print_stats()

if __name__ == "__main__":
  try:
    print(niceTime() + ': Entering main loop. Press Control-C to exit.')

    midiPi = MidiPi()

    while True:
      if Config.PROFILING:
        midiPi.profile()
        break

      midiPi.update()
      # time.sleep(0.0005)
  except:
    print(sys.exc_info())
  finally:
    MidiPorts.cleanup()
    Server.running = False
    print('Exit')