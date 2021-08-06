import adafruit_ssd1306
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import RPi.GPIO as GPIO
import time

from config import AmbientMode, Config, PendingAction, PlayMode
from menu_item import Icons, MenuItem
from music import Music
from palettes import Palette
from util import enumName

DOWN_BUTTON = 7
ENTER_BUTTON = 8
UP_BUTTON = 12

TEXT_SCROLL_DELAY = 3
DISPLAY_OFF_TIMEOUT = 30

mainMenu = [
  MenuItem('Music', items=Music.getMusic(), icon=Icons['music']),
  MenuItem('Settings', items=[
    MenuItem('Color Palette', lambda value: Config.updatePalette(value), value=lambda: Config.CURRENT_PALETTE, options=list(Palette)),
    MenuItem('Play Mode', lambda value: Config.updateValue('PLAY_MODE', value), value=lambda: Config.PLAY_MODE, options=list(PlayMode)),
    MenuItem('Ambient', items=[
      MenuItem('Ambient Mode',  lambda value: Config.updateValue('AMBIENT_MODE', value), value=lambda: Config.AMBIENT_MODE, options=list(AmbientMode)),
      MenuItem('Ambient Enabled',  lambda value: Config.updateValue('AMBIENT_ENABLED', not value), value=lambda: Config.AMBIENT_ENABLED),
      MenuItem('Night Mode',  lambda value: Config.updateValue('NIGHT_MODE_ENABLED', not value), value=lambda: Config.NIGHT_MODE_ENABLED),
      MenuItem('Night Mode Timeout',  lambda value: Config.updateValue('NIGHT_MODE_TIMEOUT', value), value=lambda: Config.NIGHT_MODE_TIMEOUT, options=[10, 20, 30, 60]),
      MenuItem('Cycle Speed',  lambda value: Config.updateValue('CYCLE_SPEED', value), value=lambda: Config.CYCLE_SPEED, options=[0.05, 0.15, 0.3, 0.75, 1, 2]),
    ])
  ]),
  MenuItem('System', items=[
    MenuItem('Shutdown', lambda: Config.updateValue('PENDING_ACTION', PendingAction.SHUTDOWN), icon=Icons['shutdown']),
    MenuItem('Reboot', lambda: Config.updateValue('PENDING_ACTION', PendingAction.REBOOT), icon=Icons['reboot']),
    MenuItem('Restart Service', lambda: Config.updateValue('PENDING_ACTION', PendingAction.RESTART_SERVICE), icon=Icons['restart'])
  ], icon=Icons['system']),
]

class Display:
  def __init__(self):
    self.displayOn = False
    self.lastButton = time.time()

    self.dirty = True
    self.textScroll = 0
    self.textTimer = time.time()

    self.menu = [{'scroll': 0, 'items': mainMenu}]
    self.updatedMenu = None

    # Set up GPIO Pins
    GPIO.setup(DOWN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENTER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(UP_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(DOWN_BUTTON, GPIO.FALLING, callback=self.button_callback, bouncetime=300)
    GPIO.add_event_detect(ENTER_BUTTON, GPIO.FALLING, callback=self.button_callback, bouncetime=300)
    GPIO.add_event_detect(UP_BUTTON, GPIO.FALLING, callback=self.button_callback, bouncetime=300)

    # Init i2c bus
    i2c = busio.I2C(SCL, SDA)

    # Create the SSD1306 OLED class.
    self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    self.disp.rotate(2)

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

  def off(self):
    # Clear display.
    self.disp.fill(0)
    self.disp.show()

  # Handle when a button is pressed
  def button_callback(self, channel):
    self.lastButton = time.time()

    if self.displayOn:
      menuSection = self.menu[len(self.menu) - 1]
      items = list(filter(lambda i: i.visible() if i.visible != None else True, menuSection['items']))

      if channel == UP_BUTTON:
        menuSection['scroll'] -= 1
      elif channel == DOWN_BUTTON:
        menuSection['scroll'] += 1
      elif channel == ENTER_BUTTON:
        selected = items[menuSection['scroll']]

        if len(selected.items) > 0:
          self.updatedMenu = self.menu + [{'scroll': 1, 'items': [MenuItem('Back', parent=selected)] + selected.items}]
        elif len(selected.options) > 0:
          scroll = 1
          if selected.value != None: scroll = selected.options.index(selected.value()) + 1

          options = list(map(lambda i: MenuItem(enumName(i), selected.onSelect, value=lambda: i, parent=selected), selected.options))
          self.updatedMenu = self.menu + [{'scroll': scroll, 'items': [MenuItem('Back', parent=selected)] + options}]
        else:
          if selected.onSelect != None and selected.value != None: selected.onSelect(selected.value())
          elif selected.onSelect != None: selected.onSelect()

          if selected.parent: self.back()

      menuSection['scroll'] = menuSection['scroll'] % len(items)

    self.textTimer = time.time() + TEXT_SCROLL_DELAY
    self.textScroll = 0
    self.dirty = True

  def back(self):
    self.updatedMenu = self.menu[:]
    self.updatedMenu.pop()

  def triangle(self, top=15, left=116, color=1):
    self.draw.polygon([(left, top), (left, top + 6), (left + 5, top + 3)], fill=color)

  def update(self):
    # Turn off the display after 30 seconds, keep track of previous to force a refresh
    prevDisplayOn = self.displayOn
    self.displayOn = time.time() - self.lastButton < DISPLAY_OFF_TIMEOUT

    if self.updatedMenu:
      self.menu = self.updatedMenu
      self.textScroll = 0
      self.textTimer = time.time() + TEXT_SCROLL_DELAY
      self.updatedMenu = None
      self.dirty = True

    if Config.DIRTY:
      self.textScroll = 0
      self.textTimer = time.time() + TEXT_SCROLL_DELAY

    menuSection = self.menu[len(self.menu) - 1]

    items = list(filter(lambda i: i.visible() if i.visible != None else True, menuSection['items']))
    if Config.SCROLL != None:
      menuSection['scroll'] = Config.SCROLL
      Config.SCROLL = None
    scroll = menuSection['scroll'] % len(items) # just in case there are less items and we need to wrap from filtered values

    selectedLabel = items[scroll].label
    if items[scroll].value != None and items[scroll].showValue: selectedLabel = items[scroll].value()
    selectedLabel = selectedLabel.replace('_', ' ').title()

    textScrolling = False
    if len(selectedLabel) > 17 and self.displayOn and time.time() > self.textTimer:
      self.textScroll += 3
      self.textTimer = time.time() + 0.6
      self.dirty = True
      textScrolling = True

    if self.dirty or Config.DIRTY or prevDisplayOn != self.displayOn:
      # Draw a black filled box to clear the image.
      self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

      if self.displayOn:
        # Selction rectangle
        self.draw.rectangle((0, 12, self.width, 21), fill=1)

        x = 10
        y = 1
        i = 0

        if len(items) > 1:
          toShow = [(scroll - 1) % len(items), scroll, (scroll + 1) % len(items)]
        else:
          toShow = [0]
          y += 10
          i = 1

        for v in toShow:
          item = items[v]

          label = item.label
          if item.value != None and item.showValue: label = item.value()
          label = label.replace('_', ' ').title()

          if i == 1 and len(label) > 17:
            label += '     '
            offset = self.textScroll % len(label)
            labelStart = label[0 : offset]
            labelEnd = label[offset :]
            self.draw.text((x, y), labelEnd + labelStart, font=self.font, fill=0)
          else:
            self.draw.text((x, y), label, font=self.font, fill=0 if i == 1 else 1)

          self.draw.rectangle((115, y + 1, self.width, y + 10), fill=1 if i == 1 else 0)

          icon = None
          if len(item.items) > 0: icon = Icons['triangle']
          if label == 'Back': icon = Icons['back']
          if item.value != None:
            if item.parent != None and item.parent.value != None and item.parent.value() == item.value(): icon = Icons['check']
            elif item.value() == True and type(item.value()) == bool: icon = Icons['check']
          if item.icon != None: icon = item.icon

          if icon != None:
            icon = ImageOps.invert(icon.convert('RGB')).convert('P') if i == 1 else icon
            self.image.paste(icon, (116, y + 1, 116 + 10, y + 11))

          y += 10
          i += 1

      self.disp.image(self.image)

      # self.disp.fill_rect(0, 12, self.width, 10, 1)
      # self.disp.text('Testing String Here', 10, 13, 0, size=1)
      self.disp.show()

    Config.DIRTY = False
    self.dirty = False