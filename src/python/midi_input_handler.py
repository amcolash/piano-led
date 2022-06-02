from rtmidi.midiconstants import NOTE_ON, PROGRAM_CHANGE
from threading import Thread
import random
import sys
import time

from config import Config, PlayMode
from i2c import I2C
from leds import Leds
from palettes import Palettes
import util

class MidiInputHandler(object):
  def __init__(self, port, midi_out_piano, midi_out_system, midi_lock):
    self.port = port
    self.wallclock = time.time()
    self.midi_out_piano = midi_out_piano
    self.midi_out_system = midi_out_system
    self.midi_lock = midi_lock
    self.colorIndex = 0

  def __call__(self, event, data=None):
    message, deltatime = event
    self.wallclock += deltatime
    # print("[%s] @%0.6f %r" % (self.port, self.wallclock, message))

    # clamp velocity to make things a bit quieter
    if len(message) > 2: message[2] = min(80, message[2])

    # If we want to forward midi to piano and got an event
    if self.midi_out_piano and self.midi_out_piano.is_port_open():
      try:
        self.midi_lock.acquire()
        self.midi_out_piano.send_message(message)
        self.midi_lock.release()
      except:
        print(util.niceTime() + ': ' + str(sys.exc_info()))

        print('Attempting to close port and stop music')
        Config.STOP_MUSIC = True
        self.midi_out_piano.close_port()

    # Strip channel from message - all channels will be played
    event = message[0] >> 4

    note = message[1]

    # Only handle ON (0b1001) and OFF (0b1000) events on ANY channel
    if (event == 0b1001 or event == 0b1000) and note >= Config.MIN_KEY and note <= Config.MAX_KEY:
      # print("[%s] @%0.6f %r %s" % (self.port, self.wallclock, message, is_on))
      velocity = message[2]

      # Forward piano midi messages to leonardo
      if not Config.CHORDS and not self.midi_out_piano:
        sendMessage = Thread(target=self.sendI2C, args=[message])
        sendMessage.start()

      is_on = event == 0b1001 and velocity > 0

      # Handle Chord Mode
      if Config.CHORDS and Config.CHORDS_ENABLED:
        if self.midi_out_system and self.midi_out_system.is_port_open():
          # Turn on display if it was off
          Config.DISPLAY_ON_FORCE = True

          note1 = note + (4 if Config.CHORDS_MAJOR else 3)
          note2 = note + 7

          # Play note an octave down
          note3 = note - 12

          allNotes = [ 'C ', 'C#', 'D ', 'D#', 'E ', 'F ', 'F#', 'G ', 'G#', 'A ', 'A#', 'B ' ]
          note1Name = allNotes[note % 12]
          note2Name = allNotes[note1 % 12]
          note3Name = allNotes[note2 % 12]

          if is_on:
            Config.CHORDS_NOTES = note1Name + "  " + note2Name + "  " + note3Name
            # print(Config.CHORDS_NOTES)
            # print(str(note) + " " + str(note1) + " " + str(note2))

          try:
            # Change to nicer piano program on channel 0
            self.midi_out_system.send_message([PROGRAM_CHANGE, 2])

            # Send actual notes
            time.sleep(random.uniform(0.0005, 0.002))
            vel1 = int(random.uniform(0.85, 1.15) * velocity)
            self.midi_out_system.send_message([NOTE_ON, note1, vel1])

            time.sleep(random.uniform(0.0005, 0.002))
            vel2 = int(random.uniform(0.85, 1.15) * velocity)
            self.midi_out_system.send_message([NOTE_ON, note2, vel2])

            time.sleep(random.uniform(0.0005, 0.002))
            vel3 = int(random.uniform(0.85, 1.15) * velocity)
            self.midi_out_system.send_message([NOTE_ON, note3, vel3])

            # When turning off notes, also turn off the opposite for major/minor to prevent hanging notes
            if not is_on:
              time.sleep(random.uniform(0.0005, 0.002))

              note4 = note + (3 if Config.CHORDS_MAJOR else 4)
              vel4 = int(random.uniform(0.85, 1.15) * velocity)
              self.midi_out_system.send_message([NOTE_ON, note4, vel4])
          except:
            print(util.niceTime() + ': ' + str(sys.exc_info()))

      # Normal LED Order
      key = (note - Config.MIN_KEY)

      led = int((key / (Config.TOTAL_KEYS + 1)) * Config.LED_COUNT)

      toUpdate = [led, led + 1]

      # Default to target2
      mainLed = Leds.leds[led]
      newColor = mainLed['target2']

      # next color in cycle
      if Config.PLAY_MODE == PlayMode.CYCLE_COLORS:
        newColor = Palettes.hsv_to_rgb_int(self.colorIndex / 360, 1, 0.3)
        self.colorIndex = (self.colorIndex + 10) % 360

      # brighten current color (assume max ambient rgb of about 20)
      elif Config.PLAY_MODE == PlayMode.BRIGHTEN_CURRENT:
        newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in mainLed['target1']]

      elif Config.PLAY_MODE == PlayMode.RIPPLE:
        # toUpdate = []
        mainLed['ripple'] = is_on
        for i in range(led - Config.RIPPLE_KEYS, led + Config.RIPPLE_KEYS):
          if i >= 0 and i < Config.LED_COUNT and i not in toUpdate:
            toUpdate.append(i)

      # Always show leds even in night mode when manually played. Only trigger leds from midi music when night mode off
      if not self.midi_out_piano or not util.nightModeActive():
        Leds.lastPlayed = time.time()

      for i in toUpdate:
        if i >= 0 and i < Config.LED_COUNT:
          updateLed = Leds.leds[i]

          try:
            if is_on:
              updateLed['state'].append(led)
            else:
              updateLed['state'].remove(led)
          except:
            # print(util.niceTime() + ': ' + str(sys.exc_info()))
            x = 1

          if len(updateLed['state']) == 0:
            updateLed['ripple'] = False

          # print(str(i) + ', ' + str(updateLed['state']))

          if Config.PLAY_MODE == PlayMode.RIPPLE:
            if updateLed['target1'] != [0,0,0]: newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in updateLed['target1']]
            else: newColor = [min(255, c * Config.BRIGHTEN_AMOUNT) for c in Config.PALETTE[i]]

          updateLed['target2'] = newColor
          updateLed['playTime'] = Leds.lastPlayed

  def sendI2C(self, message):
    try:
      I2C.bus.write_i2c_block_data(Config.I2C_MIDI_ADDRESS, 0, message)
      I2C.bus.write_quick(Config.I2C_MIDI_ADDRESS)
    except OSError:
      if Config.DEBUG_I2C: print(util.niceTime() + ' [I2C]: ' + str(sys.exc_info()))