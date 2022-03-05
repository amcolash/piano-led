import glob
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import random
import sys
import time
from urllib.parse import urlparse, parse_qs

from config import Config
from midi_ports import MidiPorts
from music import Music, musicRoot
from palettes import Palette
from power import Power
import util

hostName = "0.0.0.0"

class GetRequest:
  def __init__(self, path, handler, contentType="application/json"):
    self.path = path
    self.contentType = contentType
    self.handler = handler

GetRequests = {
  '/brightness': GetRequest('/brightness', lambda req: brightness(req)),
  '/exit': GetRequest('/exit', lambda req: exit(req)),
  '/files': GetRequest('/files', lambda req: files(req)),
  '/next': GetRequest('/next', lambda req: next(req)),
  '/nightMode': GetRequest('/nightMode', lambda req: nightMode(req)),
  '/palette': GetRequest('/palette', lambda req: palette(req)),
  '/play': GetRequest('/play', lambda req: play(req)),
  '/power': GetRequest('/power', lambda req: power(req)),
  '/status': GetRequest('/status', lambda req: status(req)),
  '/stop': GetRequest('/stop', lambda req: stop(req)),
  '/volume': GetRequest('/volume', lambda req: volume(req)),
  '*': GetRequest('/', lambda req: other(req), 'application/html')
}

def brightness(req):
  query = parse_qs(req.query)

  if 'value' in query:
    val = max(0, min(20, int(query['value'][0])))
    Config.updateValue('MAX_AMBIENT_BRIGHTNESS', val)

    return status(req, "Setting brightness to " + str(val))
  else:
    return status(req, "No brightness specified")

def exit(req):
  print(util.niceTime() + ': Server Shutdown!')
  os._exit(1)

def files(req):
  folders = Music.getFolders()
  files = {}

  for f in folders:
    folderFiles = list(glob.glob(f + '/**/*.mid', recursive=True))
    folderFiles.sort()
    files[f] = folderFiles

  return bytes(json.dumps({ 'files': files, 'musicRoot': musicRoot }), "utf-8")

def next(req):
  if len(Music.playlist) > 0: song = Path(Music.playlist[0]).stem
  Music.stop(clear=False)

  return status(req, "Skipping to next song", song)

def palette(req):
  query = parse_qs(req.query)

  if 'value' in query:
    p = query['value'][0]
    Config.updatePalette(getattr(Palette, p))
    return status(req, "Changing palette to: " + str(p))
  else:
    return status(req, "No palette selected")

def play(req):
  folder = musicRoot
  file = None

  query = parse_qs(req.query)
  if 'folder' in query:
    folder = query['folder'][0]

  if 'file' in query:
    file = query['file'][0]

  Music.queue(folder, file)

  return status(req, "Starting music: " + str(file or '') + ', ' + str(folder or ''), Path(file).stem if file != None else None)

def status(req, message=None, song=None):
  currentSong = song
  if currentSong == None and Music.nowPlaying != None: currentSong = Path(Music.nowPlaying).stem
  if currentSong == None and len(Music.playlist) > 0: currentSong = Path(Music.playlist[0]).stem

  return bytes(json.dumps({
    'on': MidiPorts.pianoOn(),
    'brightness': Config.MAX_AMBIENT_BRIGHTNESS,
    'music': currentSong,
    'volume': MidiPorts.userVolume,
    'palettes': list(map(lambda p: p.name, list(Palette))),
    'playStart': Music.startTime,
    'musicDuration': Music.duration,
    'message': message,
    'nightMode': Config.NIGHT_MODE_ENABLED,
    # 'playlist': [Music.nowPlaying] + Music.playlist,
  }), "utf-8")

def nightMode(req):
  Config.NIGHT_MODE_ENABLED = not Config.NIGHT_MODE_ENABLED
  return status(req, "Toggling night mode")

def power(req):
  query = parse_qs(req.query)

  if 'value' in query:
    on = bool(query['value'][0])

    if on:
      Power.on()
      return status(req, "Turning on power")
    else:
      Power.off()
      return status(req, "Turning off power")

  else:
    Power.toggle()
    return status(req, "Toggling power")

def stop(req):
  Music.stop()

  query = parse_qs(req.query)
  if 'off' in query:
    Power.off()

  return status(req, "Stopping music")

def volume(req):
  query = parse_qs(req.query)

  if 'value' in query:
    vol = float(query['value'][0])
    MidiPorts.updateVolume(vol, MidiPorts.musicVolume)

    return status(req, "Setting volume to " + str(vol))
  else:
    return status(req, "No volume specified")

def other(req):
  return [
    bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"),
    bytes("<p>Request: %s</p>" % req.path, "utf-8"),
    bytes("<body>", "utf-8"),
    bytes("<p>This is an example web server.</p>", "utf-8"),
    bytes("</body></html>", "utf-8")
  ]

class Server(BaseHTTPRequestHandler):
  webserver = None
  running = True

  @classmethod
  def init(cls):
    cls.webServer = HTTPServer((hostName, Config.PORT), Server)
    print("Server started http://%s:%s" % (hostName, Config.PORT))

    try:
      while cls.running:
        cls.webServer.handle_request()
    except:
      print(util.niceTime() + ': ' + str(sys.exc_info()))

    cls.webServer.server_close()
    print("Server stopped.")

  def do_GET(self):
    try:
      parsed = urlparse(self.path)
      requestHandler = GetRequests[parsed.path] if parsed.path in GetRequests else GetRequests['*']

      response = requestHandler.handler(parsed)

      self.send_response(200)
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Content-Type", requestHandler.contentType)
      self.end_headers()

      if not isinstance(response, list):
        response = [response]

      for r in response:
        self.wfile.write(r)

    except:
      print(util.niceTime() + ': ' + str(sys.exc_info()))
      self.send_response(500)
      self.end_headers()
