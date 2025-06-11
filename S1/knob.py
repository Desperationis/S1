from gpiozero import RotaryEncoder, Button


class Knob:
    def __init__(self, minimum, maximum):
        self.encoder = RotaryEncoder(a=13, b=19)
        self.button = Button(26)
        self.already_pressed = False
        self.minimum = minimum
        self.maximum = maximum

        self.value = 0
        self.encoder.when_rotated_clockwise = self.when_rotated_clockwise
        self.encoder.when_rotated_counter_clockwise = self.when_rotated_counter_clockwise

    def when_rotated_clockwise(self):
        self.value = min(self.maximum, self.value + 1)

    def when_rotated_counter_clockwise(self):
        self.value = max(self.minimum, self.value - 1)

    def get_position(self):
        return self.value

    def is_pressed(self):
        return self.button.is_pressed

    def is_pressed_instant(self):
        cache = self.is_pressed()
        output = cache

        if self.already_pressed:
            output = False

        self.already_pressed = cache

        return output



