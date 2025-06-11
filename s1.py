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

    def title():
        frame = Image.new("RGB", lcd.get_width_height())
        draw = ImageDraw.Draw(frame)

        draw_text(draw, "S1", (0, -10), (255,255,255))
        draw_text(draw, "Diego Contreras", (0, 10), (255,255,255))

        lcd.display_image(frame)

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

        if not hasattr(page_1, "date"):
            page_1.date = "n/a"
            page_1.timestamp = "n/a"
        if CURRENT_STATE == KNOB_CHANGES_PAGES:
            string_date, string_time = clock.get_date_time()
            page_1.date = string_date
            page_1.timestamp = string_time

        draw_text(draw, "Select Data Type", (0, -40), (255,0,0))
        draw_text(draw, page_1.date, (0, -20), (255,255,255))
        draw_text(draw, page_1.timestamp, (0, -0), (255,255,255))


        FEELINGS = ["relaxed", "stressed", "craving"]
        if not hasattr(page_1, "feeling"):
            page_1.feeling = "n/a"
        if CURRENT_STATE == KNOB_CHANGES_FEELING:
            page_1.feeling = FEELINGS[knob.get_position()]
        draw_text(draw, f"feeling: {page_1.feeling}", (0, 20), (255,255,255))

        TIME = ["10s", "30s", "60s"]
        if not hasattr(page_1, "time"):
            page_1.time = "n/a"
        if CURRENT_STATE == KNOB_CHANGES_TIME:
            page_1.time = TIME[knob.get_position()]
        draw_text(draw, f"time: {page_1.time}", (0, 40), (255,255,255))

        if CURRENT_STATE == KNOB_COMMIT_CHANGES:
            print(f"Final feeling: {page_1.feeling}")
            print(f"Final time: {page_1.time}")
            with open("/home/adhoc/markers.txt", "a") as f:
                timestamp = page_1.date + " " + page_1.timestamp
                data_line = f"{timestamp}, " + f"{page_1.feeling}, {page_1.time}" + "\n"
                f.write(data_line)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            page_1.feeling = "n/a"
            page_1.time = "n/a"


        lcd.display_image(frame)



    KNOB_CHANGES_PAGES = 0
    KNOB_CHANGES_FEELING = 2
    KNOB_CHANGES_TIME = 3
    KNOB_COMMIT_CHANGES = 4
    CURRENT_STATE = 0
    NEXT_STATE = 0

    title()
    time.sleep(5)

    menu_enabled = False
    current_page = 0
    while True:
        if CURRENT_STATE == KNOB_CHANGES_PAGES:
            if knob.get_position() == 1:
                current_page = 1
            else:
                current_page = 0

        pressed = knob.is_pressed_instant()

        if CURRENT_STATE == KNOB_COMMIT_CHANGES:
            NEXT_STATE = KNOB_CHANGES_PAGES
            knob.set_min_max(0, 1) # This brings us back to the home page
            print("ENTERERD PAGES")

        if current_page == 1 and pressed:
            if CURRENT_STATE == KNOB_CHANGES_TIME:
                NEXT_STATE = KNOB_COMMIT_CHANGES

            if CURRENT_STATE == KNOB_CHANGES_FEELING:
                NEXT_STATE = KNOB_CHANGES_TIME
                knob.set_min_max(0, 2)

            if CURRENT_STATE == KNOB_CHANGES_PAGES:
                NEXT_STATE = KNOB_CHANGES_FEELING
                knob.set_min_max(0, 2)

        CURRENT_STATE = NEXT_STATE




        if current_page == 1:
            page_1()
        else:
            page_0()



finally:
    console.print("[bold red]Program exited gracefully[/bold red]")







