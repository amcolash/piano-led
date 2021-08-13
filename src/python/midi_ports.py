import rtmidi
from rtmidi.midiconstants import (ALL_SOUND_OFF, CONTROL_CHANGE, RESET_ALL_CONTROLLERS, VOLUME)
import sys
import time

from config import Config
from leds import Leds
from midi_input_handler import MidiInputHandler

# This class is a singleton

class MidiPorts:
  midiCount = 100
  currentVolume = 127
  nextVolume = 127

  midi_in_piano = rtmidi.MidiIn()
  midi_in_system = rtmidi.MidiIn()
  midi_out_piano = rtmidi.MidiOut()

  @classmethod
  def update(cls):
    # If the volume needs to be updated
    cls.updateVolume()

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
            cls.currentVolume = 0
            cls.nextVolume = 127
          else:
            if Config.DEBUG_MIDI: print('MIDI Fine')
      except:
        print(sys.exc_info())

  @classmethod
  def pianoOn(cls):
    return cls.midi_out_piano and cls.midi_out_piano.is_port_open()

  @classmethod
  def stopAll(cls):
    if cls.pianoOn():

      try:
        # Send MIDI reset message
        cls.midi_out_piano.send_message([CONTROL_CHANGE, ALL_SOUND_OFF, 0])
        cls.midi_out_piano.send_message([CONTROL_CHANGE, RESET_ALL_CONTROLLERS, 0])
      except:
        print(sys.exc_info())

    # In addition to resetting, clear LEDs
    Leds.clearLeds()

    # Wait a moment for things to settle
    time.sleep(0.005)

  @classmethod
  def updateVolume(cls):
    if cls.nextVolume != cls.currentVolume and cls.pianoOn():
      newVol = min(127, max(0, cls.nextVolume))

      try:
        # change volume for each of the 16 channels
        for c in range(15):
          # Send new MIDI volume
          cls.midi_out_piano.send_message([CONTROL_CHANGE | c, VOLUME, newVol])
          time.sleep(0.001)
      except:
        print(sys.exc_info())

      cls.currentVolume = newVol

  @classmethod
  def cleanup(cls):
    cls.stopAll()

    cls.midi_in_piano.close_port()
    cls.midi_out_piano.close_port()
    cls.midi_in_system.close_port()

    del cls.midi_in_piano
    del cls.midi_out_piano
    del cls.midi_in_system