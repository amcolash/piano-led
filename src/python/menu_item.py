import glob
from pathlib import Path
from PIL import Image

rootPath = str(Path(__file__).parent)
imgPath = str(Path(rootPath + '/../img/').resolve())

# Keep track of all of the icons
Icons = {}

def loadIcons():
  files = list(glob.glob(imgPath + '/**/*.png', recursive=True))
  for f in files:
    name = Path(f).stem
    Icons[name] = Image.open(f)

loadIcons()

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