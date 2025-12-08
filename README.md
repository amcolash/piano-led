# piano-led

LEDs for my piano!

## Requirements

- `libopenjp2-7-dev`
- `libjack-jackd2-dev`

### Dev Requirements

- `entr`

### Install everything at ounce

`sudo apt-get libopenjp2-7-dev libjack-jackd2-dev python3-pip entr`

## Python dependencies

- adafruit-circuitpython-ssd1306
- jsonpickle
- mido
- pyfluidsynth
- python-rtmidi
- pytz
- rpi_ws281x
- smbus2
- pillow

Install the dependencies as root using `sudo` Since this will likely be the only python program running on the pi, it should be fine.

`sudo pip install --break-system-packages adafruit-circuitpython-ssd1306 jsonpickle mido python-rtmidi pytz rpi_ws281x smbus2 pillow`
