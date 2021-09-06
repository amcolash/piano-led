import glob
import mido
from pathlib import Path

rootPath = str(Path(__file__).parent)
musicRoot = str(Path(rootPath + '/../midi').resolve())

def getMidiVelocity(file):
  mid = mido.MidiFile(file)

  vels = {}
  total_avg = 0
  i = 1

  for track in mid.tracks:
    avg_vel = 0
    j = 0

    for msg in track:
      if msg.type == 'note_on':
        vel = msg.velocity
        if vel > 0:
          j += 1
          avg_vel = (avg_vel * (j - 1) + vel) / j

    if avg_vel > 0:
      name = track.name or 'Piano'

      if name in vels: vels[name + ' '] = avg_vel
      else: vels[name] = avg_vel

      total_avg = (total_avg * (i - 1) + avg_vel) / i
      i += 1

  return total_avg


file_vels = {}
file_avg = 0
i = 1


files = glob.glob(musicRoot + '/**/*.mid', recursive=True)
for f in files:
  avg = getMidiVelocity(f)
  file_vels[f] = avg

  file_avg = (file_avg * (i - 1) + avg) / i
  i += 1

print(file_avg)

for f in files:
  play_vol = 2 - (file_vels[f] / file_avg)
  print(f, file_vels[f], play_vol, play_vol / 2)