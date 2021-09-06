from mido import MidiFile
import time

mid = MidiFile("Daniel Powter - Bad Day.mid")

start = time.time()
print(start)

print(mid.length)

print(time.time() - start)
