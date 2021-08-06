import glob
from pathlib import Path
import random
import subprocess

from config import Config
from menu_item import Icons, MenuItem
from midi_ports import MidiPorts

rootPath = str(Path(__file__).parent)
musicRoot = str(Path(rootPath + '/../../midi').resolve())

class Music:
  nowPlaying = None
  playlist = []
  process = None

  @classmethod
  def queue(cls, folder=None, file=None):
    if cls.process != None:
      Music.stop()

    if folder != None:
      cls.playlist = list(glob.glob(folder + '/**/*.mid', recursive=True))
      random.shuffle(cls.playlist) # always shuffled for now
    elif file != None:
      cls.playlist = [file]

    Config.SCROLL = 1

  @classmethod
  def play(cls, file):
    print('Playing: ' + file)

    if cls.process != None:
      Music.stop()
    else:
      MidiPorts.stopAll()

    cls.nowPlaying = file
    cls.process = subprocess.Popen(['aplaymidi', '--port=System MIDI In', file],
      stdout=subprocess.PIPE,
      universal_newlines=True)

    Config.DIRTY = True

  @classmethod
  def stop(cls):
    print('Stopped Music')
    cls.nowPlaying = None
    cls.playlist = []

    if cls.process != None:
      cls.process.terminate()
      cls.process = None

    MidiPorts.stopAll()
    Config.DIRTY = True
    Config.SCROLL = 1

  @classmethod
  def update(cls):
    if len(cls.playlist) > 0 and cls.process == None:
      Music.play(cls.playlist.pop(0))
    elif cls.process == None:
      cls.nowPlaying = None
      # Config.DIRTY = True

    try:
      if cls.process != None:
        # Do something else
        return_code = cls.process.poll()
        if return_code is not None:
          # print('RETURN CODE', return_code)
          # # Process has finished, read rest of the output
          # for output in cls.process.stdout.readlines():
          #   print(output.strip())
          cls.process = None
    except:
      print('Something went wrong checking process!')
      if cls.process != None:
        cls.process.terminate()
        cls.process = None

  @classmethod
  def getFiles(cls, folder, parent):
    files = list(glob.glob(folder + '/**/*.mid', recursive=True))
    files.sort()

    items = [MenuItem('Shuffle', lambda: Music.queue(folder=folder), icon=Icons['shuffle'], parent=parent)]
    items += list(map(lambda f: MenuItem(Path(f).stem, lambda value: Music.queue(file=value), value=lambda: f, parent=parent), files))

    return items

  @classmethod
  def getMusic(cls):
    folders = list(glob.glob(musicRoot + '/*'))
    folders.sort()

    menu = [
      MenuItem('Now Playing', icon=Icons['speaker'], value=lambda: Path(cls.nowPlaying).stem if cls.nowPlaying != None else None, visible=lambda: cls.nowPlaying != None, showValue=True),
      MenuItem('Shuffle', lambda: Music.queue(folder=musicRoot), icon=Icons['shuffle']),
      MenuItem('Stop', lambda: Music.stop(), icon=Icons['stop'], visible=lambda: cls.nowPlaying != None)
    ]

    # can't use map since we are passing in the parent
    for f in folders:
      item = MenuItem(Path(f).stem, None, value=lambda: f, visible=lambda: cls.nowPlaying == None)
      item.items = Music.getFiles(f, item)
      menu.append(item)

    return menu