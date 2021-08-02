import glob
from pathlib import Path
import random
import subprocess

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

  @classmethod
  def play(cls, file):
    print('Playing: ' + file)

    if cls.process != None:
      Music.stop()

    cls.nowPlaying = file
    cls.process = subprocess.Popen(['aplaymidi', '--port=System MIDI In', file],
      stdout=subprocess.PIPE,
      universal_newlines=True)

  @classmethod
  def stop(cls):
    print('stop')
    cls.nowPlaying = None
    cls.playlist = []

    if cls.process != None:
      cls.process.terminate()
      cls.process = None

    MidiPorts.stopAll()

  @classmethod
  def update(cls):
    if len(cls.playlist) > 0 and cls.process == None:
      Music.play(cls.playlist.pop(0))
    else:
      cls.nowPlaying = None

    try:
      if cls.process != None:
        # Do something else
        return_code = cls.process.poll()
        if return_code is not None:
          print('RETURN CODE', return_code)
          # Process has finished, read rest of the output
          for output in cls.process.stdout.readlines():
            print(output.strip())

          cls.process = None
    except:
      print('Something went wrong checking process!')
      if cls.process != None:
        cls.process.terminate()
        cls.process = None

  @classmethod
  def getFiles(cls, folder):
    files = list(glob.glob(folder + '/**/*.mid', recursive=True))
    files.sort()

    return [MenuItem('Shuffle', lambda: Music.queue(folder=folder), icon=Icons['shuffle'])] + list(map(lambda f: MenuItem(Path(f).stem, lambda value: Music.queue(file=value), value=lambda: f), files))

  @classmethod
  def getMusic(cls):
    folders = list(glob.glob(musicRoot + '/*'))
    folders.sort()

    menu = list(map(lambda f: MenuItem(Path(f).stem, None, value=lambda: f, items=Music.getFiles(f)), folders))
    menu = [
      MenuItem('Shuffle', lambda: Music.queue(folder=musicRoot), icon=Icons['shuffle']),
      MenuItem('Stop', lambda: Music.stop(), icon=Icons['stop'])
    ] + menu

    return menu