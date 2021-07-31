import datetime

from config import Config

def logTime(start, label):
  print(label + ': ' + str((time.time() - start) * 1000))

def niceTime():
  return str(datetime.datetime.now(Config.TIMEZONE).replace(microsecond=0)).replace('-07:00', '')

def enumName(enum):
  return enum.name.replace('_', ' ').title()