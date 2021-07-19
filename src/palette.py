# List of palettes to use. Remember to wrap the first + last colors!

fire = [
  [0, [160,0,0]],
  [0.33, [240,60,5]],
  [0.66, [255,245,60]],
  [1, [160,0,0]],
]

rgb = [
  [0, [255,0,0]],
  [0.33, [0,255,0]],
  [0.66, [0,0,255]],
  [1, [255,0,0]],
]

pink = [
  [0, [250,120,210]],
  [0.33, [125,80,200]],
  [0.66, [155,150,230]],
  [1, [250,120,210]],
]

DEFAULT = fire
MAX_BRIGHTNESS = 10

def lerp(a, b, t):
  value = a + (b-a) * t
  return int(value * (MAX_BRIGHTNESS / 255))

def lerpColor(a, b, t):
  return [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)]

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
      palette.append(lerpColor(left[1], right[1], t))

      i += 1
      percent = i / (LED_COUNT - 1)

  return palette