import fluidsynth
import pathlib
from config import Config

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
SF2_PATH = str(SCRIPT_DIR / "Yamaha C5 Grand-v2.4.sf2")

class Synth:
  if Config.FLUIDSYNTH_ENABLED:
    synth = fluidsynth.Synth()
    sfid = synth.sfload(SF2_PATH)
    synth.program_select(0, sfid, 0, 0)

    # Reduce latency
    synth.setting("audio.period-size", 64)
    synth.setting("audio.periods", 3)
    synth.setting("synth.chorus.active", False)
    synth.setting("synth.reverb.active", False)

    # Increase default gain
    synth.setting("synth.gain", 1.0)

    synth.start(driver='alsa')

  @classmethod
  def startNote(cls, note, velocity):
    cls.synth.noteon(0, note, velocity)

  @classmethod
  def stopNote(cls, note):
    cls.synth.noteoff(0, note)

  @classmethod
  def cleanup(cls):
    cls.synth.delete()
