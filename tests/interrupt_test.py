from gpiozero import Button

button = Button(7)
button.when_pressed = lambda: print("Pressed")

while True:
    pass
