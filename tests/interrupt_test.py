import RPi.GPIO as GPIO

BUTTON = 12  # Board pin number

GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, bouncetime=300)
    print("Event detection added successfully")
except RuntimeError as e:
    print(f"Error: {e}")

# Keep the program running
try:
    while True:
        if GPIO.event_detected(BUTTON):
            print("Edge detected")
except KeyboardInterrupt:
    GPIO.cleanup()
