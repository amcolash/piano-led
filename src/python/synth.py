import tinysoundfont

# This class is a singleton

class Synth:
  synth = tinysoundfont.Synth()
  synth.start("alsa")
  sfid = synth.sfload("Yamaha C5 Grand-v2.4.sf2")
  synth.program_select(0, sfid, 0, 0)

  @classmethod
  def startNote(cls, note, velocity):
    cls.synth.noteon(0, note, velocity)

  @classmethod
  def stopNote(cls, note):
    cls.synth.noteoff(0, note)

  @classmethod
  def cleanup(cls):
    cls.synth.delete()