from enum import Enum, auto

# List of palettes to use. Remember to wrap the first + last colors!
class Palette(Enum):
  Autumn = [
    [0.00, [69, 21, 21]],
    [0.33, [35, 25, 25]],
    [0.67, [98, 58, 26]],
    [1.00, [69, 21, 21]],
  ]
  Beach = [
    [0, [0,177,56]],
    [0.25, [226,168,110]],
    [0.5, [5,111,142]],
    [0.75, [6,73,163]],
    [1, [0,177,56]],
  ]
  Fire = [
    [0, [160,0,0]],
    [0.33, [240,60,5]],
    [0.66, [255,245,60]],
    [1, [160,0,0]],
  ]
  Forest = [
    [0, [106, 255, 61]],
    [0.25, [48, 90, 34]],
    [0.5, [81, 230, 68]],
    [0.75, [140, 90, 40]],
    [1, [106, 255, 61]],
  ]
  Ocean = [
    [0, [30,170,180]],
    [0.33, [0,20,250]],
    [0.66, [30,250,50]],
    [1, [30,170,180]],
  ]
  Pink = [
    [0, [250,30,60]],
    [0.33, [80,30,200]],
    [0.66, [100,70,100]],
    [1, [250,30,60]],
  ]
  Rainbow = [
    [0, [255,0,0]],
    [0.33, [0,255,0]],
    [0.66, [0,0,255]],
    [1, [255,0,0]],
  ]
  Sorbet = [
    [0, [62, 65, 137]],
    [0.25, [54, 129, 109]],
    [0.5, [210, 158, 46]],
    [0.75, [140, 79, 94]],
    [1, [62, 65, 137]],
  ]

MAX_BRIGHTNESS = 20
BRIGHTNESS_SCALAR = MAX_BRIGHTNESS / 255

def hsv_to_rgb(h, s, v):
  if s == 0.0: v*=255; return [v, v, v]
  i = int(h*6.) # XXX assume int() truncates!
  f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
  if i == 0: return [v, t, p]
  if i == 1: return [q, v, p]
  if i == 2: return [p, v, t]
  if i == 3: return [p, q, v]
  if i == 4: return [t, p, v]
  if i == 5: return [v, p, q]

def hsv_to_rgb_int(h, s, v):
  rgb = hsv_to_rgb(h, s, v)
  return [int(rgb[0]), int(rgb[1]), int(rgb[2])]

def lerp(a, b, t, scaled=False):
  if scaled: return int((a + (b-a) * t) * BRIGHTNESS_SCALAR)
  else: return int(a + (b-a) * t)

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