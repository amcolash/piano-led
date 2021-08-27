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

    return bytes("Setting brightness to " + str(val), "utf-8")
  else:
    return bytes("No brightness specified", "utf-8")

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
  Music.stop(clear=False)
  return bytes("Skipping to next song", "utf-8")

def palette(req):
  query = parse_qs(req.query)

  if 'value' in query:
    p = query['value'][0]
    Config.updatePalette(getattr(Palette, p))
    return bytes("Changing palette to: " + str(p), "utf-8")
  else:
    return bytes("No palette selected", "utf-8")

def play(req):
  folder = musicRoot
  file = None

  query = parse_qs(req.query)
  if 'folder' in query:
    folder = query['folder'][0]

  if 'file' in query:
    file = query['file'][0]

  Music.queue(folder, file)

  return bytes("Starting music: " + str(file) + ', ' + str(folder), "utf-8")

def status(req):
  song = Path(Music.nowPlaying or '').stem if Music.nowPlaying != None else None

  return bytes(json.dumps({
    'on': MidiPorts.pianoOn(),
    'brightness': Config.MAX_AMBIENT_BRIGHTNESS,
    'music': song,
    'volume': MidiPorts.currentVolume,
    'palettes': list(map(lambda p: p.name, list(Palette))),
    'playStart': Music.startTime,
    'musicDuration': Music.duration,
    # 'playlist': [Music.nowPlaying] + Music.playlist,
  }), "utf-8")

def power(req):
  Power.toggle()
  return bytes("Toggling power", "utf-8")

def stop(req):
  Music.stop()
  return bytes("Stopping music", "utf-8")

def volume(req):
  query = parse_qs(req.query)

  if 'value' in query:
    vol = int(query['value'][0])
    MidiPorts.nextVolume = vol

    return bytes("Setting volume to " + str(vol), "utf-8")
  else:
    return bytes("No volume specified", "utf-8")

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

  @classmethod
  def init(cls):
    cls.webServer = HTTPServer((hostName, Config.PORT), Server)
    print("Server started http://%s:%s" % (hostName, Config.PORT))

    try:
      cls.webServer.serve_forever()
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
