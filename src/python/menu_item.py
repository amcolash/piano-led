from pathlib import Path
from PIL import Image

rootPath = str(Path(__file__).parent)

Back = Image.open(Path(rootPath + '/../img/back.png'))
Check = Image.open(Path(rootPath + '/../img/checkmark.png'))
Music = Image.open(Path(rootPath + '/../img/music.png'))
Shuffle = Image.open(Path(rootPath + '/../img/shuffle.png'))
Stop = Image.open(Path(rootPath + '/../img/stop.png'))
Triangle = Image.open(Path(rootPath + '/../img/triangle.png'))

Icons = {
  'back': Back,
  'check': Check,
  'music': Music,
  'shuffle': Shuffle,
  'stop': Stop,
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