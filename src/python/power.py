import RPi.GPIO as GPIO
import time

POWER_PIN = 15

class Power:
  @classmethod
  def init(cls):
    # Set power pin to output
    GPIO.setup(POWER_PIN, GPIO.OUT)

    # Set default power state to off
    GPIO.output(POWER_PIN, GPIO.LOW)

  @classmethod
  def toggle(cls):
    GPIO.output(POWER_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(POWER_PIN, GPIO.LOW)