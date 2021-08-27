from threading import Thread
import sys
import time

from config import Config, PlayMode
from i2c import I2C
from leds import Leds
from palettes import Palettes
import util

class MidiInputHandler(object):
  def __init__(self, port, midi_out_piano):
    self.port = port
    self.wallclock = time.time()
    self.midi_out_piano = midi_out_piano
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
        self.midi_out_piano.send_message(message)
      except:
        print(util.niceTime() + ': ' + str(sys.exc_info()))

        print('Attempting to close port and stop music')
        Config.STOP_MUSIC = True
        self.midi_out_piano.close_port()

    # Strip channel from message - all channels will be played
    event = message[0] >> 4

    # Only handle ON (0b1001) and OFF (0b1000) events on ANY channel
    if (event == 0b1001 or event == 0b1000) and message[1] >= Config.MIN_KEY and message[1] <= Config.MAX_KEY:
      # print("[%s] @%0.6f %r %s" % (self.port, self.wallclock, message, is_on))

      # Forward piano midi messages to leonardo
      if not self.midi_out_piano:
        sendMessage = Thread(target=self.sendI2C, args=[message])
        sendMessage.start()

      velocity = message[2]
      is_on = event == 0b1001 and velocity > 0

      # Normal LED Order
      key = (message[1] - Config.MIN_KEY)

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
    except:
      if Config.DEBUG_I2C: print(util.niceTime() + ': ' + str(sys.exc_info()))