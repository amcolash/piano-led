import glob
import jsonpickle
from mido import MidiFile
from pathlib import Path
import random
import subprocess
import time

from config import Config
from menu_item import Icons, MenuItem
from midi_ports import MidiPorts
import util

rootPath = str(Path(__file__).parent)

metadataFile = Path(rootPath + '/metadata.json')
musicRoot = str(Path(rootPath + '/../../midi').resolve())

class Music:
  nowPlaying = None
  playlist = []
  process = None

  duration = 0
  startTime = 0
  avgVelocity = 0

  metadata = {}
  metadata['durations'] = {}
  metadata['veolicites'] = {}


  @classmethod
  def init(cls):
    cls.loadMetadata()
    cls.initMidiMetadata()
    cls.saveMetadata()

  @classmethod
  def loadMetadata(cls):
    # try to load existing metadata
    if metadataFile.exists():
      try:
        f = open(metadataFile, "r")
        loaded = jsonpickle.decode(f.read())

        for key in loaded.metadata['durations']:
          if Path(key).exists():
            cls.metadata['durations'][key] = loaded.metadata['durations'][key]

        for key in loaded.metadata['velocities']:
          if Path(key).exists():
            cls.metadata['velocities'][key] = loaded.metadata['velocities'][key]
      except:
        print(util.niceTime() + ': ' + str(sys.exc_info()))

  @classmethod
  def saveMetadata(cls):
    # save durations as json
    encoded = jsonpickle.encode(cls.metadata)
    with open(metadataFile, "w") as f:
      print(encoded, file=f)

  @classmethod
  def initMidiMetadata(cls):
    print('Init Music Metadata: This might take a while...')

    file_avg = 0
    i = 1

    # go through all files, if a duration does not exist, find it
    files = list(glob.glob(musicRoot + '/**/*.mid', recursive=True))
    for f in files:
      if f not in cls.metadata['durations']:
        print('Getting metadata for', f)

        mid = MidiFile(f)

        duration = mid.length
        cls.metadata['durations'][f] = duration

        avg = getMidiVelocity(mid)
        cls.metadata['velocities'][f] = avg

        print('Duration: ', duration, 'Velocity: ', avg)

      avg = cls.metadata['velocities'][f]
      file_avg = (file_avg * (i - 1) + avg) / i
      i += 1

    print('Average Velocity: ', file_avg)
    cls.avgVelocity = file_avg

  @classmethod
  def getMidiVelocity(cls, mid):
    vels = {}
    total_avg = 0
    i = 1

    for track in mid.tracks:
      avg_vel = 0
      j = 0

      for msg in track:
        if msg.type == 'note_on':
          vel = msg.velocity
          if vel > 0:
            j += 1
            avg_vel = (avg_vel * (j - 1) + vel) / j

      if avg_vel > 0:
        name = track.name or 'Piano'

        if name in vels: vels[name + ' '] = avg_vel
        else: vels[name] = avg_vel

        total_avg = (total_avg * (i - 1) + avg_vel) / i
        i += 1

    return total_avg

  @classmethod
  def queue(cls, folder=None, file=None):
    if cls.process != None:
      cls.stop()

    # Keep a temp list so the whole list is changed at once, to avoid threading issues
    p = []

    if folder != None:
      print('Queueing music in folder: ' + str(folder))
      p = list(glob.glob(folder + '/**/*.mid', recursive=True))
      random.shuffle(p) # always shuffled for now

    if file != None:
      print('Queueing file: ' + str(file))
      if folder == None:
        p = [file]
      else:
        p.insert(0, file)

    cls.playlist = p

    Config.SCROLL = 1

  @classmethod
  def play(cls, file, clear=True):
    print('Playing: ' + file)

    if cls.process != None:
      cls.stop(clear)
    else:
      MidiPorts.stopAll()

    cls.startTime = time.time()

    # Note: this won't work on new files, need to restart server to pick up any new durations (since it is slooooow)
    cls.duration = 0
    if file in cls.metadata['durations']:
      cls.duration = cls.metadata['durations'][file]

    cls.nowPlaying = file
    cls.process = subprocess.Popen(['aplaymidi', '--port=System MIDI In', file],
      stdout=subprocess.PIPE,
      universal_newlines=True)

    Config.DIRTY = True

  @classmethod
  def stop(cls, clear=True):
    print('Stopped Music')
    cls.nowPlaying = None
    if clear: cls.playlist = []

    if cls.process != None:
      cls.process.terminate()
      cls.process = None

    MidiPorts.stopAll()
    Config.DIRTY = True
    Config.SCROLL = 1

  @classmethod
  def update(cls):
    if Config.STOP_MUSIC:
      Config.STOP_MUSIC = False
      cls.stop()

    if len(cls.playlist) > 0 and cls.process == None and MidiPorts.midi_in_system.is_port_open():
      cls.play(cls.playlist.pop(0))
    elif cls.process == None:
      cls.nowPlaying = None
      # Config.DIRTY = True

    try:
      if cls.process != None:
        return_code = cls.process.poll()

        if return_code is not None:
          cls.process = None
    except:
      print('Something went wrong checking process!')
      print(util.niceTime() + ': ' + str(sys.exc_info()))
      if cls.process != None:
        cls.process = None
        cls.process.terminate()

  @classmethod
  def getFiles(cls, folder, parent):
    files = list(glob.glob(folder + '/**/*.mid', recursive=True))
    files.sort()

    items = [MenuItem('Shuffle', lambda: cls.queue(folder=folder), icon=Icons['shuffle'], parent=parent)]
    items += list(map(lambda f: MenuItem(Path(f).stem, lambda value: cls.queue(file=value), value=lambda: f, parent=parent), files))

    return items

  @classmethod
  def getFolders(cls):
    folders = list(glob.glob(musicRoot + '/*'))
    folders.sort()
    return folders

  @classmethod
  def getMusic(cls):
    folders = cls.getFolders()

    menu = [
      MenuItem('Now Playing', icon=Icons['speaker'], value=lambda: Path(cls.nowPlaying).stem if cls.nowPlaying != None else None, visible=lambda: cls.nowPlaying != None, showValue=True),
      MenuItem('Shuffle', lambda: cls.queue(folder=musicRoot), icon=Icons['shuffle']),
      MenuItem('Stop', lambda: cls.stop(), icon=Icons['stop'], visible=lambda: cls.nowPlaying != None)
    ]

    # can't use map since we are passing in the parent
    for f in folders:
      item = MenuItem(Path(f).stem.title(), None, value=lambda: f, visible=lambda: cls.nowPlaying == None)
      item.items = cls.getFiles(f, item)
      menu.append(item)

    return menu