import fluidsynth
import pathlib
from config import Config
import subprocess

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
SF2_PATH = str(SCRIPT_DIR / "Yamaha C5 Grand-v2.4.sf2")

class Synth:
  sfid = None
  synth = None

  @classmethod
  def init(cls):
    if Config.FLUIDSYNTH_ENABLED:
      print("Initializing FluidSynth")

      if cls.synth:
        cls.cleanup()

      cls.synth = fluidsynth.Synth()
      cls.sfid = cls.synth.sfload(SF2_PATH)
      cls.synth.program_select(0, cls.sfid, 0, 0)

      # Reduce latency
      cls.synth.setting("audio.period-size", 64)
      cls.synth.setting("audio.periods", 3)
      cls.synth.setting("synth.chorus.active", False)
      cls.synth.setting("synth.reverb.active", False)

      # Increase default gain
      cls.synth.setting("synth.gain", 1.0)

      cls.synth.start(driver='alsa')

  @classmethod
  def startNote(cls, note, velocity):
    cls.synth.noteon(0, note, velocity)

  @classmethod
  def stopNote(cls, note):
    cls.synth.noteoff(0, note)

  @classmethod
  def cleanup(cls):
    if cls.synth:
      print("Cleaning up FluidSynth")
      if cls.sfid is not None:
        cls.synth.sfunload(cls.sfid)

      cls.synth.delete()
      cls.synth = None
      cls.sfid = None

      # Force any lingering ALSA processes to be stopped
      try:
        subprocess.run(['sudo', 'fuser', '-k', '/dev/snd/*'], capture_output=True)
      except:
        pass