import adafruit_ssd1306
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import time

from config import AmbientMode, Config, PlayMode
from palettes import Palette


BUTTON1 = 13
BUTTON2 = 19
BUTTON3 = 26

class Display:
  def __init__(self):
    self.displayOn = False
    self.debounce = time.time()

    # TODO: Move menu to a new class?
    self.menu = [ 'Palette', 'Play', 'Ambient' ]
    self.scroll = 0
    self.dirty = True

    # Set up GPIO Pins
    GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON1, GPIO.FALLING, callback=self.button_callback)
    GPIO.add_event_detect(BUTTON2, GPIO.FALLING, callback=self.button_callback)
    GPIO.add_event_detect(BUTTON3, GPIO.FALLING, callback=self.button_callback)

    # Init i2c bus
    i2c = busio.I2C(SCL, SDA)

    # Create the SSD1306 OLED class.
    self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

    # Clear display.
    self.disp.fill(0)
    self.disp.show()

    self.disp.contrast(1)

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    self.width = self.disp.width
    self.height = self.disp.height
    self.image = Image.new("1", (self.width, self.height))

    # Get drawing object to draw on image.
    self.draw = ImageDraw.Draw(self.image)

    # Load default font.
    self.font = ImageFont.load_default()

  # Handle when a button is pressed
  def button_callback(self, channel):
    if time.time() - self.debounce > 0.25:
      if self.displayOn:
        if channel == BUTTON3:
          self.scroll -= 1
        elif channel == BUTTON1:
          self.scroll += 1
        elif channel == BUTTON2:
          # TODO: Make enum selection generic
          if self.menu[self.scroll] == 'Palette':
            pals = list(Palette)
            current = pals.index(Config.CURRENT_PALETTE)
            Config.TO_UPDATE['CURRENT_PALETTE'] = pals[(current + 1) % len(pals)]
            # Config.updatePalette(pals[(current + 1) % len(pals)])
          elif self.menu[self.scroll] == 'Play':
            mode = list(PlayMode)
            current = mode.index(Config.PLAY_MODE)
            Config.TO_UPDATE['PLAY_MODE'] = mode[(current + 1) % len(mode)]
            # Config.PLAY_MODE = mode[(current + 1) % len(mode)]
          elif self.menu[self.scroll] == 'Ambient':
            mode = list(AmbientMode)
            current = mode.index(Config.AMBIENT_MODE)
            Config.TO_UPDATE['AMBIENT_MODE'] = mode[(current + 1) % len(mode)]
            # Config.AMBIENT_MODE = mode[(current + 1) % len(mode)]
            # Config.PALETTE_DIRTY = 3 # force a color palette refresh when changing ambient modes

      self.dirty = True
      self.debounce = time.time()

    self.scroll = self.scroll % len(self.menu)

  def update(self):
    # Turn off the display after 30 seconds, keep track of previous to force a refresh
    prevDisplayOn = self.displayOn
    self.displayOn = time.time() - self.debounce < 30

    if self.dirty or Config.DIRTY or prevDisplayOn != self.displayOn:
      # Draw a black filled box to clear the image.
      self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

      if self.displayOn:
        toShow = [(self.scroll - 1) % len(self.menu), self.scroll, (self.scroll + 1) % len(self.menu)]

        x = 10
        y = 2
        for i in toShow:
          value = ""

          if self.menu[i] == 'Palette':
            value = Config.CURRENT_PALETTE.name
          elif self.menu[i] == 'Play':
            value = Config.PLAY_MODE.name
          elif self.menu[i] == 'Ambient':
            value = Config.AMBIENT_MODE.name

          self.draw.text((x, y), self.menu[i] + ": " + value, font=self.font, fill=1)
          y += 10

        # scrollTop = scroll * 8 + 2
        scrollTop = 15
        self.draw.polygon([(0,scrollTop), (0, scrollTop + 6), (5,scrollTop + 3)], fill=1)

      self.disp.image(self.image)
      self.disp.show()

      Config.DIRTY = False
      self.dirty = False