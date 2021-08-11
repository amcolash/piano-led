from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import sys
import time

from config import Config
from music import Music, musicRoot

hostName = "0.0.0.0"

class GetRequest:
  def __init__(self, path, handler, contentType="application/json"):
    self.path = path
    self.contentType = contentType
    self.handler = handler

GetRequests = {
  '/play': GetRequest('/play', lambda: play(), "application/text"),
  '/stop': GetRequest('/stop', lambda: stop(), "application/text"),
  '/music': GetRequest('/music', lambda: music(), "application/text"),
  '/folders': GetRequest('/folders', lambda: folders()),
  '*': GetRequest('/', lambda: other(), "application/html")
}

def play():
  Music.queue(folder=musicRoot)
  return bytes("Starting music", "utf-8")

def stop():
  Music.stop()
  return bytes("Stopping music", "utf-8")

def music():
  song = Path(Music.nowPlaying or '').stem
  return bytes(song, "utf-8")

def folders():
  return bytes(json.dumps(Music.getFolders()), "utf-8")

def other():
  return [
    bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"),
    bytes("<p>Request: %s</p>" % self.path, "utf-8"),
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
    except KeyboardInterrupt:
      pass

    cls.webServer.server_close()
    print("Server stopped.")

  def do_GET(self):
    try:
      requestHandler = GetRequests[self.path] or GetRequests['*']
      response = requestHandler.handler()

      self.send_response(200)
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Content-Type", requestHandler.contentType)
      self.end_headers()

      self.wfile.write(response)

    except:
      print(sys.exc_info())
      self.send_response(500)