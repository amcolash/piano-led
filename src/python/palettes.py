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

Ocean = [
  [0, [30,170,180]],
  [0.33, [0,20,250]],
  [0.66, [30,250,50]],
  [1, [30,170,180]],
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