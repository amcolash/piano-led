import CHIP_IO.GPIO as GPIO
import ctypes

libc = ctypes.CDLL('libc.so.6')

PIN = "PWM0"

GPIO.setup(PIN, GPIO.OUT)

def high():
  GPIO.output(PIN, GPIO.HIGH)
  libc.usleep(0.8)
  GPIO.output(PIN, GPIO.LOW)
  libc.usleep(0.45)

def low():
  GPIO.output(PIN, GPIO.HIGH)
  libc.usleep(0.4)
  GPIO.output(PIN, GPIO.LOW)
  libc.usleep(0.85)

while True:
  for x in range(3):
    for bit in range(72):
      high()

  libc.usleep(50)


