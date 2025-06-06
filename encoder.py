from gpiozero import RotaryEncoder, Button

encoder = RotaryEncoder(a=13, b=19)
button = Button(26)

while True:
    print("Position:", encoder.steps)
    if button.is_pressed:
        print("Button pressed!")

