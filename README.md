# piano-led

LEDs for my piano!

## Requirements

- `RPi-GPIO` - installed by default
- `libopenjp2-7-dev`
- `libjack-jackd2-dev`

### NOTE: On New PiOS versions, you need to remove the legacy version of this in favor of the newer version
```
sudo apt remove python3-rpi.gpio
sudo apt install python3-rpi-lgpio
```

### Dev Requirements

- entr (`sudo apt install entr`)

### Combined

`sudo apt remove python3-rpi.gpio && sudo apt-get install python3-rpi-lgpio libopenjp2-7-dev libjack-jackd2-dev entr`

## Python Dependencies can be installed with `pip`.

Install pip if necessary

`sudo apt install python3-pip`

Then install the dependencies as root using `sudo` Since this will likely be the only python program, it should be fine :fingers-crossed:.

`sudo pip install --break-system-packages adafruit-circuitpython-ssd1306 jsonpickle mido python-rtmidi pytz rpi_ws281x smbus2 pillow`

- adafruit-circuitpython-ssd1306
- jsonpickle
- mido
- python-rtmidi
- pytz
- rpi_ws281x
- smbus2
- pillow
