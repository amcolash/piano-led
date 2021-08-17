import glob
from pathlib import Path
import random
import subprocess

from config import Config
from menu_item import Icons, MenuItem
from midi_ports import MidiPorts
import util

rootPath = str(Path(__file__).parent)
musicRoot = str(Path(rootPath + '/../../midi').resolve())

class Music:
  nowPlaying = None
  playlist = []
  process = None

  @classmethod
  def queue(cls, folder=None, file=None):
    if cls.process != None:
      cls.stop()

    if folder != None:
      print('Queueing music in folder: ' + str(folder))
      cls.playlist = list(glob.glob(folder + '/**/*.mid', recursive=True))
      random.shuffle(cls.playlist) # always shuffled for now

    if file != None:
      print('Queueing file: ' + str(file))
      if folder == None:
        cls.playlist = [file]
      else:
        cls.playlist.insert(0, file)

    Config.SCROLL = 1

  @classmethod
  def play(cls, file, clear=True):
    print('Playing: ' + file)

    if cls.process != None:
      cls.stop(clear)
    else:
      MidiPorts.stopAll()

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