import time

from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

        #with midiout:
            #note_on = [NOTE_ON, 60, 112] # channel 1, middle C, velocity 112
            #note_off = [NOTE_OFF, 60, 0]
            #midiout.send_message(note_on)
            #time.sleep(0.5)
            #midiout.send_message(note_off)
            #time.sleep(0.1)
        midiout.send_message(message)

midiout, port_name = open_midioutput(1)
midiin, port_name = open_midiinput(1)

midiin.set_callback(MidiInputHandler(port_name))

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
    del midiout

