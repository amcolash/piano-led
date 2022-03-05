import datetime
from enum import Enum
import io
from pathlib import Path
from subprocess import call
import sys

from config import Config, PendingAction

rootPath = str(Path(__file__).parent)
scriptRoot = str(Path(rootPath + '/../../scripts').resolve())

def logTime(start, label):
  print(label + ': ' + str((time.time() - start) * 1000))

def niceTime():
  return str(datetime.datetime.now(Config.TIMEZONE).replace(microsecond=0)).replace('-07:00', '')

def enumName(enum):
  if isinstance(enum, Enum):
    return enum.name.replace('_', ' ').title()
  else:
    return str(enum)

def updatePendingActions(Disp):
  if Config.PENDING_ACTION != PendingAction.NONE:
    Disp.off()

    if Config.PENDING_ACTION == PendingAction.SHUTDOWN:
      call("sudo shutdown -h now", shell=True)
    elif Config.PENDING_ACTION == PendingAction.REBOOT:
      call("sudo reboot now", shell=True)
    elif Config.PENDING_ACTION == PendingAction.RESTART_SERVICE:
      call(scriptRoot + "/restart.sh reboot now", shell=True)

    sys.exit(0)

def is_raspberrypi():
  try:
    with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
      if 'raspberry pi' in m.read().lower(): return True
  except Exception: pass
  return False

def nightModeActive():
  hour = datetime.datetime.now(Config.TIMEZONE).hour
  minute = datetime.datetime.now(Config.TIMEZONE).minute

  current = hour + minute / 60

  start = Config.NIGHT_MODE_START_HOUR + Config.NIGHT_MODE_START_MINUTE / 60
  end = Config.NIGHT_MODE_END_HOUR + Config.NIGHT_MODE_START_MINUTE / 60

  return Config.NIGHT_MODE_ENABLED and current >= start and current < end