from http.server import BaseHTTPRequestHandler, HTTPServer
import time

from config import Config
from music import Music, musicRoot

hostName = "0.0.0.0"

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
    if self.path == '/play':
      self.send_response(200)
      self.end_headers()
      Music.queue(folder=musicRoot)
      self.wfile.write(bytes("Starting music", "utf-8"))

    elif self.path == '/stop':
      self.send_response(200)
      self.end_headers()
      Music.stop()
      self.wfile.write(bytes("Stopping music", "utf-8"))

    elif self.path == '/music':
      self.send_response(200)
      self.end_headers()
      self.wfile.write(bytes("Now Playing: " + str(Music.nowPlaying), "utf-8"))

    else:
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
      self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
      self.wfile.write(bytes("<body>", "utf-8"))
      self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
      self.wfile.write(bytes("</body></html>", "utf-8"))