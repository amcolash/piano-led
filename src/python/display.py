import adafruit_ssd1306
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import RPi.GPIO as GPIO
import time

from config import AmbientMode, Config, PlayMode
from menu_item import Icons, MenuItem
from palettes import Palette
from util import enumName

BUTTON1 = 13
BUTTON2 = 19
BUTTON3 = 26

mainMenu = [
  MenuItem('Nested', icon=Icons['triangle'], items=[
    MenuItem('Color Palette', lambda value: Config.updatePalette(value), value=lambda: Config.CURRENT_PALETTE, options=list(Palette)),
    MenuItem('Play Mode', lambda value: Config.updateValue('PLAY_MODE', value), value=lambda: Config.PLAY_MODE, options=list(PlayMode)),
    MenuItem('Ambient Mode',  lambda value: Config.updateValue('AMBIENT_MODE', value), value=lambda: Config.AMBIENT_MODE, options=list(AmbientMode)),
  ])
]

class Display:
  def __init__(self):
    self.displayOn = False
    self.lastButton = time.time()

    self.dirty = True

    self.menu = [{'scroll': 0, 'items': mainMenu}]
    self.updatedMenu = None

    # Set up GPIO Pins
    GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON1, GPIO.FALLING, callback=self.button_callback, bouncetime=300)
    GPIO.add_event_detect(BUTTON2, GPIO.FALLING, callback=self.button_callback, bouncetime=300)
    GPIO.add_event_detect(BUTTON3, GPIO.FALLING, callback=self.button_callback, bouncetime=300)

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
    self.lastButton = time.time()

    if self.displayOn:
      menuSection = self.menu[len(self.menu) - 1]

      if channel == BUTTON3:
        menuSection['scroll'] -= 1
      elif channel == BUTTON1:
        menuSection['scroll'] += 1
      elif channel == BUTTON2:
        selected = menuSection['items'][menuSection['scroll']]

        if len(selected.items) > 0:
          self.updatedMenu = self.menu + [{'scroll': 1, 'items': [MenuItem('Back', icon=Icons['back'])] + selected.items}]
        elif len(selected.options) > 0:
          scroll = 1
          if selected.value != None: scroll = selected.options.index(selected.value()) + 1

          options = list(map(lambda i: MenuItem(enumName(i), selected.onSelect, value=lambda: i, parent=selected), selected.options))
          self.updatedMenu = self.menu + [{'scroll': scroll, 'items': [MenuItem('Back', icon=Icons['back'])] + options}]
        else:
          if selected.onSelect != None and selected.value != None: selected.onSelect(selected.value())
          self.back()

      menuSection['scroll'] = menuSection['scroll'] % len(menuSection['items'])

    self.dirty = True

  def back(self):
    self.updatedMenu = self.menu[:]
    self.updatedMenu.pop()

  def triangle(self, top=15, left=116, color=1):
    self.draw.polygon([(left, top), (left, top + 6), (left + 5, top + 3)], fill=color)

  def update(self):
    # Turn off the display after 30 seconds, keep track of previous to force a refresh
    prevDisplayOn = self.displayOn
    self.displayOn = time.time() - self.lastButton < 30

    if self.dirty or Config.DIRTY or prevDisplayOn != self.displayOn or self.updatedMenu != None:
      if self.updatedMenu:
        self.menu = self.updatedMenu
        self.updatedMenu = None

      # Draw a black filled box to clear the image.
      self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

      if self.displayOn:
        # Selction rectangle
        self.draw.rectangle((0, 11, self.width, 22), outline=0, fill=1)

        menuSection = self.menu[len(self.menu) - 1]

        x = 10
        y = 1
        i = 0

        if len(menuSection['items']) > 1:
          toShow = [(menuSection['scroll'] - 1) % len(menuSection['items']), menuSection['scroll'], (menuSection['scroll'] + 1) % len(menuSection['items'])]
        else:
          toShow = [0]
          y += 10
          i = 1

        for v in toShow:
          item = menuSection['items'][v]

          self.draw.text((x, y), item.label, font=self.font, fill=1 if i != 1 else 0)

          icon = item.icon
          if item.parent != None and item.parent.value != None and item.value != None:
            if item.parent.value() == item.value(): icon = Icons['check']

          if icon != None:
            icon = ImageOps.invert(icon.convert('RGB')).convert('P') if i == 1 else icon
            self.image.paste(icon, (116, y + 1, 116 + 10, y + 11))

          y += 10
          i += 1

      self.disp.image(self.image)
      self.disp.show()

      Config.DIRTY = False
      self.dirty = False