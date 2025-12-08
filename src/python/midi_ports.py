import rtmidi
from rtmidi.midiconstants import (ALL_SOUND_OFF, CONTROL_CHANGE, END_OF_EXCLUSIVE, LOCAL_CONTROL, RESET_ALL_CONTROLLERS, SYSTEM_EXCLUSIVE)
import sys
from threading import Lock
import time

from config import Config
from leds import Leds
from midi_input_handler import MidiInputHandler
import util

MAX_VOLUME = 16383

# This class is a singleton

class MidiPorts:
  midiCount = 100
  userVolume = 0
  musicVolume = 0

  midi_in_piano = rtmidi.MidiIn()
  midi_in_system = rtmidi.MidiIn()
  midi_out_piano = rtmidi.MidiOut()
  midi_out_system = rtmidi.MidiOut()

  midi_lock = Lock()

  @classmethod
  def update(cls):
    if cls.midiCount > 0:
      cls.midiCount -= 1
    else:
      try:
        cls.midiCount = 100

        if not cls.midi_in_system.is_port_open():
          port_name = cls.midi_in_system.open_port(0)
          cls.midi_in_system.set_callback(MidiInputHandler(port_name, cls.midi_out_piano, None, cls.midi_lock))
          cls.midi_in_system.set_client_name('System MIDI In')

          cls.midi_out_system.open_port(0)
          cls.midi_out_system.set_client_name('System MIDI Out')

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
            cls.midi_in_piano.set_callback(MidiInputHandler(port_name, None, cls.midi_out_system, cls.midi_lock))
            cls.midi_in_piano.set_client_name('Piano MIDI In')

            cls.midi_out_piano.open_port(1)
            cls.midi_out_piano.set_client_name('Piano MIDI Out')
            cls.updateVolume(1, 1)
            cls.updateLocalMode()
          else:
            if Config.DEBUG_MIDI: print('MIDI Fine')
      except:
        print(util.niceTime() + ': ' + str(sys.exc_info()))

  @classmethod
  def pianoOn(cls):
    return cls.midi_out_piano and cls.midi_out_piano.is_port_open()

  @classmethod
  def stopAll(cls):
    if cls.pianoOn():

      try:
        cls.midi_lock.acquire()

        # Send MIDI reset message
        cls.midi_out_piano.send_message([CONTROL_CHANGE, ALL_SOUND_OFF, 0])
        cls.midi_out_piano.send_message([CONTROL_CHANGE, RESET_ALL_CONTROLLERS, 0])

        cls.midi_lock.release()
      except:
        print(util.niceTime() + ': ' + str(sys.exc_info()))

    # In addition to resetting, clear LEDs
    Leds.clearLeds()

    # Wait a moment for things to settle
    time.sleep(0.005)

  @classmethod
  def updateVolume(cls, userVolume, musicVolume):
    if cls.pianoOn():
      newVol = int(min(MAX_VOLUME, max(0, userVolume * musicVolume * MAX_VOLUME)))

      # Split into low/high bits of 14 bit value
      low = newVol & 0x7B
      high = newVol >> 7

      # Send master MIDI device volume message based off of: https://www.recordingblogs.com/wiki/midi-master-volume-message
      try:
        cls.midi_lock.acquire()
        cls.midi_out_piano.send_message([SYSTEM_EXCLUSIVE, 0x7F, 0x7F, 0x04, 0x01, low, high, END_OF_EXCLUSIVE])
        cls.midi_lock.release()
      except:
        print(util.niceTime() + ': ' + str(sys.exc_info()))

      cls.userVolume = userVolume
      cls.musicVolume = musicVolume

  @classmethod
  def updateLocalMode(cls):
    if cls.pianoOn():
      try:
        cls.midi_lock.acquire()
        cls.midi_out_piano.send_message([CONTROL_CHANGE, LOCAL_CONTROL, 0x7f if Config.FLUIDSYNTH_ENABLED else 0x00])
        cls.midi_lock.release()
      except:
        print(util.niceTime() + ': ' + str(sys.exc_info()))

  @classmethod
  def cleanup(cls):
    cls.stopAll()

    cls.midi_in_piano.close_port()
    cls.midi_out_piano.close_port()
    cls.midi_in_system.close_port()

    del cls.midi_in_piano
    del cls.midi_out_piano
    del cls.midi_in_system
