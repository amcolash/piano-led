import rtmidi
import sys

from config import Config
from midi_input_handler import MidiInputHandler

# This class is a singleton

class MidiPorts:
  midiCount = 100
  midi_in_piano = rtmidi.MidiIn()
  midi_in_system = rtmidi.MidiIn()
  midi_out_piano = rtmidi.MidiOut()

  @classmethod
  def update(cls):
    if cls.midiCount > 0:
      cls.midiCount -= 1
    else:
      try:
        cls.midiCount = 100

        if not cls.midi_in_system.is_port_open():
          port_name = cls.midi_in_system.open_port(0)
          cls.midi_in_system.set_callback(MidiInputHandler(port_name, cls.midi_out_piano))
          cls.midi_in_system.set_client_name('System MIDI In')

        ports = cls.midi_in_piano.get_ports()
        keyboard_present = any(Config.MIDI_DEVICE in string for string in ports)

        if not keyboard_present:
          if cls.midi_in_piano.is_port_open():
            if Config.DEBUG_MIDI: print('Closing old port')
            cls.midi_in_piano.close_port()
            cls.midi_out_piano.close_port()
          else:
            if Config.DEBUG_MIDI: print('No Device')
        else:
          if not cls.midi_in_piano.is_port_open():
            if Config.DEBUG_MIDI: print('Init MIDI')
            port_name = cls.midi_in_piano.open_port(1)
            cls.midi_in_piano.set_callback(MidiInputHandler(port_name, None))
            cls.midi_in_piano.set_client_name('Piano MIDI In')

            cls.midi_out_piano.open_port(1)
            cls.midi_out_piano.set_client_name('Piano MIDI Out')
          else:
            if Config.DEBUG_MIDI: print('MIDI Fine')
      except:
        print(sys.exc_info())

  @classmethod
  def stopAll(cls):
    if cls.midi_out_piano and cls.midi_out_piano.is_port_open():
      for c in range(15):
        command = (0b1000 << 4) + c # note off for each of the 16 channels
        for n in range(127):
          cls.midi_out_piano.send_message([command, n, 0])

  @classmethod
  def cleanup(cls):
    cls.stopAll()

    cls.midi_in_piano.close_port()
    cls.midi_out_piano.close_port()
    cls.midi_in_system.close_port()

    del cls.midi_in_piano
    del cls.midi_out_piano
    del cls.midi_in_system