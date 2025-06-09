import qwiic_rv8803
import sys
import time

class Clock:
    def __init__(self):
        self.rtc = qwiic_rv8803.QwiicRV8803()
        if self.rtc.is_connected() == False:
            print("The device isn't connected to the system. Please check your connection", \
                file=sys.stderr)
            exit(1)

        self.rtc.begin()

    def get_date_time(self) -> (str, str):
        self.rtc.update_time()
        return (self.rtc.string_date_usa(), self.rtc.string_time())

    def set_clock_to_system(self):
        self.rtc.set_time_zone_quarter_hours(0) # Make sure t1he time zone is zero, otherwise getEpoch will be offset
        self.rtc.set_epoch(time.time()) # set with Unix Epoch for GMT: Wednesday, November 27, 2024 7:40:38 PM




if __name__ == '__main__':
    c = Clock()
    c.set_clock_to_system()
    print(f"New clock: {c.get_date_time()}")

