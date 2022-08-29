import requests
import time
from leds import Leds
import values

CALENDAR_ON = False
TIMER_DURATION = 60 * 3

# Named Cal to avoid import issues
class Cal:
  @classmethod
  def update(cls):
    global CALENDAR_ON

    newValue = None

    if time.time() - Leds.lastPlayed > TIMER_DURATION and CALENDAR_ON:
      # Turn Off Calendar
      print("Turning Off Calendar")
      CALENDAR_ON = False
      newValue = '0'

    if time.time() - Leds.lastPlayed < TIMER_DURATION and not CALENDAR_ON:
      # Turn On Calendar
      print("Turning On Calendar")
      CALENDAR_ON = True
      newValue = '1'

    if newValue:
      url = values.TUYA_SERVER + '/device/' + values.CALENDAR_ID + '?value=' + newValue

      try:
        response = requests.post(url)
      except requests.exceptions.RequestException as e:
        print(e)