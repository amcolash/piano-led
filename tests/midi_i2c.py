import time

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
from smbus2 import SMBus

I2C_ADDRESS = 8

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

        if message[2] > 0:
          bus.write_i2c_block_data(I2C_ADDRESS, 0, [255,0,0])
          bus.write_i2c_block_data(I2C_ADDRESS, 3, [0,255,0])
          bus.write_i2c_block_data(I2C_ADDRESS, 6, [0,0,255])
        else:
          bus.write_i2c_block_data(I2C_ADDRESS, 0, [0,0,0])
          bus.write_i2c_block_data(I2C_ADDRESS, 3, [0,0,0])
          bus.write_i2c_block_data(I2C_ADDRESS, 6, [0,0,0])

midiin, port_name = open_midiinput(1)
midiin.set_callback(MidiInputHandler(port_name))

bus = SMBus(1)

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin