class MenuItem:
  def __init__(self, label, onSelect=None, value=None, options=[], items=[]):
    self.label = label
    self.onSelect = onSelect
    self.value = value
    self.options = options
    self.items = items

  def __repr__(self):
    return self.label