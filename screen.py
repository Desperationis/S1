import board
import digitalio
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735
import colorsys

# Configuration for CS, DC, and RST pins:
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D20)
reset_pin = digitalio.DigitalInOut(board.D21)

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the display object:
disp = st7735.ST7735R(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    width=128,
    height=128,
    x_offset=1, y_offset=3,
    rotation=90
)

# Create a new image with RGB mode
width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Draw a vertical rainbow gradient
for y in range(height):
    # Calculate color for this row
    # HSV to RGB conversion for smooth rainbow
    hue = y / height
    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.5, 1)]
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# Display the image
disp.image(image)
import time
from PIL import Image, ImageDraw, ImageFont
import colorsys

# Assuming disp, width, and height are already defined and initialized

font = ImageFont.load_default()
text = "Bouncy!"
text_width, text_height = font.getbbox(text)[2:4]

x, y = 0, 0
vx, vy = 2, 2  # Adjust speed as desired

while True:
    frame = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(frame)

    # Draw rainbow background
    for row in range(height):
        hue = row / height
        r, g, b = [int(val * 255) for val in colorsys.hsv_to_rgb(hue, 1, 1)]
        draw.line([(0, row), (width, row)], fill=(r, g, b))

    # Draw the text
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    # Display the frame
    disp.image(frame)

    # Update position
    x += vx
    y += vy

    # Bounce off edges
    if x < 0 or x + text_width > width:
        vx = -vx
        x += vx
    if y < 0 or y + text_height > height:
        vy = -vy
        y += vy

