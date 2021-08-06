import datetime
from enum import Enum
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
  if Config.PENDING_ACTION != None:
    Disp.off()

    if Config.PENDING_ACTION == PendingAction.SHUTDOWN:
      call("sudo shutdown -h now", shell=True)
    elif Config.PENDING_ACTION == PendingAction.REBOOT:
      call("sudo reboot now", shell=True)
    elif Config.PENDING_ACTION == PendingAction.RESTART_SERVICE:
      call(scriptRoot + "/restart.sh reboot now", shell=True)

    sys.exit(0)