from PIL import Image, ImageDraw, ImageFont
from S1 import *
from rich import inspect
from rich.console import Console
import signal

ecg_log_path = "/home/adhoc/ecg_log.txt"
heart_log_path = "/home/adhoc/heart_log.txt"

console = Console()

polar = Polar(ecg_log=ecg_log_path, heart_log=heart_log_path)
clock = Clock()
lcd = LCD()
knob = Knob(0, 1)

def handle_exit(signum, frame):
    console.print("[bold red]Received exit signal[/bold red]")
    polar.exit_event.set()
    exit(1)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

try:
    font = ImageFont.load_default()

    def draw_text(draw, string, offset_center, color):
        text_width, text_height = font.getbbox(string)[2:4]
        x = 128/2 - text_width/2 + offset_center[0]
        y = 128/2 - text_height/2 + offset_center[1]
        draw.text((x, y), string, font=font, fill=color)

    def page_0():
        frame = Image.new("RGB", lcd.get_width_height())
        draw = ImageDraw.Draw(frame)

        hr_data = f"HR: {polar.CUR_HEART_RATE} HRV: {polar.CUR_HRV} ms"
        draw_text(draw, hr_data, (0, 0), (255,255,255))

        string_date, string_time = clock.get_date_time()
        draw_text(draw, string_date, (0, -40), (255,255,255))
        draw_text(draw, string_time, (0, -20), (255,255,255))

        draw_text(draw, f"ecg: {size_of_file(ecg_log_path)}", (0, 20), (255,255,255))
        draw_text(draw, f"rhr: {size_of_file(heart_log_path)}", (0, 40), (255,255,255))

        lcd.display_image(frame)

    def page_1():
        frame = Image.new("RGB", lcd.get_width_height())
        draw = ImageDraw.Draw(frame)
        draw_text(draw, f"bleh", (0, 0), (255,255,255))


        lcd.display_image(frame)


    while True:
        if knob.get_position() == 1:
            page_1()
        else:
            page_0()



finally:
    console.print("[bold red]Program exited gracefully[/bold red]")







