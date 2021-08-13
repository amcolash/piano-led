from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import random
import sys
import time
from urllib.parse import urlparse, parse_qs

from config import Config
from midi_ports import MidiPorts
from music import Music, musicRoot
from palettes import Palette

hostName = "0.0.0.0"

class GetRequest:
  def __init__(self, path, handler, contentType="application/json"):
    self.path = path
    self.contentType = contentType
    self.handler = handler

GetRequests = {
  '/next': GetRequest('/next', lambda req: next(req)),
  '/palette': GetRequest('/palette', lambda req: palette(req)),
  '/play': GetRequest('/play', lambda req: play(req)),
  '/status': GetRequest('/status', lambda req: status(req)),
  '/stop': GetRequest('/stop', lambda req: stop(req)),
  '/volume': GetRequest('/volume', lambda req: volume(req)),
  '*': GetRequest('/', lambda req: other(req), 'application/html')
}

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
  f = musicRoot

  query = parse_qs(req.query)
  if 'folder' in query: f = query['folder'][0]

  Music.queue(folder=f)
  return bytes("Starting music in folder: " + str(f), "utf-8")

def status(req):
  song = Path(Music.nowPlaying or '').stem if Music.nowPlaying != None else None

  return bytes(json.dumps({
    'on': MidiPorts.pianoOn(), 'music': song, 'musicRoot': musicRoot, 'folders': Music.getFolders(), 'volume': MidiPorts.currentVolume,
    'playlist': [Music.nowPlaying] + Music.playlist, 'palettes': list(map(lambda p: p.name, list(Palette)))
  }), "utf-8")

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
      print(sys.exc_info())

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
      print(sys.exc_info())
      self.send_response(500)