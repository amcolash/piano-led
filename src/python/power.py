from gpiozero import DigitalOutputDevice
from midi_ports import MidiPorts
import time

POWER_PIN = 15

class Power:
  @classmethod
  def init(cls):
    # Set power pin to output
    cls.power = DigitalOutputDevice(POWER_PIN, initial_value=False)

  @classmethod
  def toggle(cls):
    cls.power.on()
    time.sleep(0.5)
    cls.power.off()

  @classmethod
  def on(cls):
    if not MidiPorts.pianoOn():
      cls.toggle()

  @classmethod
  def off(cls):
    if MidiPorts.pianoOn():
      cls.toggle()
