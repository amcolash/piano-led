import time
import spidev

spi = spidev.SpiDev()
spi.open(32766, 0)
to_send = [0x01, 0x02, 0x03]

try:
    while True:
        spi.xfer(to_send)
except KeyboardInterrupt:
    print('interrupted!')
