import time

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import RPi.GPIO as GPIO

BUTTON1 = 13
BUTTON2 = 19
BUTTON3 = 26

class Display:
  def __init__(self):
    self.displayOn = False
    self.debounce = time.time()

    # TODO: Move menu to a new class?
    self.menu = [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'  ]
    self.scroll = 0
    self.selected = 0

    # Set up GPIO Pins
    GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON1,GPIO.FALLING,callback=self.button_callback)
    GPIO.add_event_detect(BUTTON2,GPIO.FALLING,callback=self.button_callback)
    GPIO.add_event_detect(BUTTON3,GPIO.FALLING,callback=self.button_callback)

    # Init i2c bus
    i2c = busio.I2C(SCL, SDA)

    # Create the SSD1306 OLED class.
    self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

    # Clear display.
    self.disp.fill(0)
    self.disp.show()

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
          self.selected = self.scroll

      self.debounce = time.time()

    self.scroll = self.scroll % len(self.menu)

  def update(self):
    # Draw a black filled box to clear the image.
    self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    # Turn off the display after 10 seconds
    self.displayOn = time.time() - self.debounce < 10

    if self.displayOn:
      toShow = [(self.scroll - 1) % len(self.menu), self.scroll, (self.scroll + 1) % len(self.menu)]

      x = 10
      y = 2
      for i in toShow:
        self.draw.text((x, y), self.menu[i], font=self.font, fill=1)
        y += 10

      self.draw.text((40, 12), self.menu[self.selected], font=self.font, fill=1)

      # scrollTop = scroll * 8 + 2
      scrollTop = 15
      self.draw.polygon([(0,scrollTop), (0, scrollTop + 6), (5,scrollTop + 3)], fill=1)

    self.disp.image(self.image)
    self.disp.show()
