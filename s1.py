from PIL import Image, ImageDraw, ImageFont
from S1 import *
from rich import inspect
from rich.console import Console
import signal

console = Console()

polar = Polar()
clock = Clock()
lcd = LCD()

def handle_exit(signum, frame):
    console.print("[bold red]Received exit signal[/bold red]")
    polar.exit_event.set()
    exit(1)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

try:
    font = ImageFont.load_default()
    while True:
        frame = Image.new("RGB", lcd.get_width_height())
        draw = ImageDraw.Draw(frame)

        text = f"HR: {polar.CUR_HEART_RATE} HRV: {polar.CUR_HRV} ms"
        text_width, text_height = font.getbbox(text)[2:4]
        x, y = 128/2 - text_width/2, 128/2 - text_height/2

        # Draw the text
        draw.text((x, y), text, font=font, fill=(255, 255, 255))


        string_date, string_time = clock.get_date_time()

        text_width, text_height = font.getbbox(string_date)[2:4]
        x, y = 128/2 - text_width/2, 128/2 - text_height/2 - 40
        draw.text((x, y), string_date, font=font, fill=(255, 255, 255))

        text_width, text_height = font.getbbox(string_time)[2:4]
        x, y = 128/2 - text_width/2, 128/2 - text_height/2 - 20
        draw.text((x, y), string_time, font=font, fill=(255, 255, 255))


        # Display the frame
        lcd.display_image(frame)



finally:
    console.print("[bold red]Program exited gracefully[/bold red]")








