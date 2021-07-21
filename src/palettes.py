# List of palettes to use. Remember to wrap the first + last colors!

Fire = [
  [0, [160,0,0]],
  [0.33, [240,60,5]],
  [0.66, [255,245,60]],
  [1, [160,0,0]],
]

RGB = [
  [0, [255,0,0]],
  [0.33, [0,255,0]],
  [0.66, [0,0,255]],
  [1, [255,0,0]],
]

Pink = [
  [0, [250,30,60]],
  [0.33, [80,30,200]],
  [0.66, [100,70,100]],
  [1, [250,30,60]],
]

MAX_BRIGHTNESS = 20
BRIGHTNESS_SCALAR = MAX_BRIGHTNESS / 255

def lerp(a, b, t, scaled=False):
  value = a + (b-a) * t
  if scaled: return int(value * BRIGHTNESS_SCALAR)
  else: return int(value)

def lerpColor(a, b, t, scaled=False):
  return [lerp(a[0], b[0], t, scaled), lerp(a[1], b[1], t, scaled), lerp(a[2], b[2], t, scaled)]

def generatePalette(gradient, LED_COUNT):
  palette = []
  i = 0

  for step in range(len(gradient) - 1):
    left = gradient[step]
    right = gradient[step + 1]

    percent = i / (LED_COUNT - 1)
    while percent <= right[0]:
      t = (percent - left[0]) / (right[0] - left[0])
      # palette.append([i, step, t, lerpColor(left[1], right[1], t)])
      palette.append(lerpColor(left[1], right[1], t, True))

      i += 1
      percent = i / (LED_COUNT - 1)

  return palette