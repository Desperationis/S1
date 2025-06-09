import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735
import colorsys


class LCD:
    def __init__(self):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D20)
        reset_pin = digitalio.DigitalInOut(board.D21)
        spi = board.SPI()

        # Maxed out settings -> Highest refresh rate
        self.disp = st7735.ST7735R(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            width=128,
            height=128,
            x_offset=1, y_offset=3,
            rotation=90,
            baudrate=24000000
        )

    def display_image(self, img):
        self.disp.image(img)

    def get_width_height(self) -> (int, int):
        return (self.disp.width, self.disp.height)



