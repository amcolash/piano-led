from pathlib import Path
from PIL import Image

rootPath = str(Path(__file__).parent)

Back = Image.open(Path(rootPath + '/../img/back.png'))
Check = Image.open(Path(rootPath + '/../img/checkmark.png'))
Music = Image.open(Path(rootPath + '/../img/music.png'))
Reboot = Image.open(Path(rootPath + '/../img/reboot.png'))
Restart = Image.open(Path(rootPath + '/../img/restart.png'))
Shuffle = Image.open(Path(rootPath + '/../img/shuffle.png'))
Shutdown = Image.open(Path(rootPath + '/../img/shutdown.png'))
Speaker = Image.open(Path(rootPath + '/../img/speaker.png'))
Stop = Image.open(Path(rootPath + '/../img/stop.png'))
System = Image.open(Path(rootPath + '/../img/system.png'))
Triangle = Image.open(Path(rootPath + '/../img/triangle.png'))

Icons = {
  'back': Back,
  'check': Check,
  'music': Music,
  'reboot': Reboot,
  'restart': Restart,
  'shuffle': Shuffle,
  'shutdown': Shutdown,
  'speaker': Speaker,
  'stop': Stop,
  'system': System,
  'triangle': Triangle,
}

class MenuItem:
  def __init__(self, label, onSelect=None, value=None, icon=None, options=[], items=[], parent=None, visible=None, showValue=False):
    self.label = label # label for the item
    self.onSelect = onSelect # function when selected, (value) => {}
    self.value = value # function to get current value, () => value
    self.icon = icon # icon from icon list above
    self.options = options # a list of options to select from for a value
    self.items = items # a list of MenuItems
    self.parent = parent # parent MenuItem
    self.visible = visible # function to check if the item is visible in the list
    self.showValue = showValue # if the MenuItem should instead show value

  def __repr__(self):
    return str(self.value()) if self.value != None and self.showValue else self.label