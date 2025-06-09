import asyncio
import threading
from typing import Union
from bleak import BleakScanner
from rich.console import Console
from rich import inspect
import numpy as np
import neurokit2 as nk
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

from polar_python import (
    PolarDevice,
    MeasurementSettings,
    SettingType,
    ECGData,
    ACCData,
    HRData,
)

console = Console()

class Polar:
    def __init__(self):
        self.ecg_data_list = []
        self.CUR_HEART_RATE = 0
        self.CUR_HRV = 0
        self.exit_event = threading.Event()
        self.loop_ready = threading.Event()
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()
        self.loop_ready.wait()  # Wait until the loop is running
        # Schedule the main coroutine safely
        asyncio.run_coroutine_threadsafe(self.main(), self.loop)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop_ready.set()
        self.loop.run_forever()

    def close(self):
        self.exit_event.set()
        # Stop the event loop safely
        def stopper():
            self.loop.stop()
        self.loop.call_soon_threadsafe(stopper)
        self.loop_thread.join()

    async def main(self):
        device = await BleakScanner.find_device_by_filter(
            lambda bd, ad: bd.name and "Polar H10" in bd.name, timeout=5
        )
        if device is None:
            console.print("[bold red]Device not found[/bold red]")
            return

        inspect(device)

        print("f")
        async with PolarDevice(device) as polar_device:
            print("a")
            available_features = await polar_device.available_features()
            inspect(available_features)

            for feature in available_features:
                print("waiting on response...")
                settings = await polar_device.request_stream_settings(feature)
                console.print(f"[bold blue]Settings for {feature}:[/bold blue] {settings}")

            print("g")
            ecg_settings = MeasurementSettings(
                measurement_type="ECG",
                settings=[
                    SettingType(type="SAMPLE_RATE", array_length=1, values=[130]),
                    SettingType(type="RESOLUTION", array_length=1, values=[14]),
                ],
            )

            acc_settings = MeasurementSettings(
                measurement_type="ACC",
                settings=[
                    SettingType(type="SAMPLE_RATE", array_length=1, values=[25]),
                    SettingType(type="RESOLUTION", array_length=1, values=[16]),
                    SettingType(type="RANGE", array_length=1, values=[2]),
                ],
            )

            polar_device.set_callback(self.data_callback, self.heartrate_callback)
            print("t")

            await polar_device.start_stream(ecg_settings)
            await polar_device.start_stream(acc_settings)

            print("g")
            await polar_device.start_heartrate_stream()

            print("h")
            while not self.exit_event.is_set():
                print("waiting")
                await asyncio.sleep(1)

    def heartrate_callback(self, data: HRData):
        print(f"Heart Rate: {int(data.heartrate)}")
        self.CUR_HEART_RATE = int(data.heartrate)

    def data_callback(self, data: Union[ECGData, ACCData]):
        if isinstance(data, ECGData):
            self.ecg_data_list.extend(data.data)

            if len(self.ecg_data_list) > 2500:
                samples_in_minute = 60 * 130
                cut = samples_in_minute * 1
                start_index = int(max(0, len(self.ecg_data_list) - cut))

                peaks, info = nk.ecg_peaks(self.ecg_data_list[start_index:], sampling_rate=130)

                # --- Begin MAD Filter Addition ---
                rpeaks = np.where(peaks == 1)[0]
                rr_intervals = np.diff(rpeaks) / 130 * 1000  # ms

                def mad_filter(rr, threshold=3.5, window=11):
                    rr_series = pd.Series(rr)
                    rolling_median = rr_series.rolling(window, center=True, min_periods=1).median()
                    mad = (rr_series - rolling_median).abs().rolling(window, center=True, min_periods=1).median()
                    outliers = ((rr_series - rolling_median).abs() > threshold * mad)
                    rr_filtered = rr_series.copy()
                    rr_filtered[outliers] = rolling_median[outliers]
                    return rr_filtered.values

                rr_filtered = mad_filter(rr_intervals)

                filtered_rpeaks = [rpeaks[0]]
                for rr in rr_filtered:
                    filtered_rpeaks.append(filtered_rpeaks[-1] + int(rr / 1000 * 130))
                filtered_peaks = np.zeros_like(peaks)
                filtered_rpeaks = np.array(filtered_rpeaks, dtype=int)
                filtered_rpeaks = filtered_rpeaks[filtered_rpeaks < len(filtered_peaks)]
                filtered_peaks[filtered_rpeaks] = 1
                # --- End MAD Filter Addition ---

                hrv = nk.hrv(filtered_peaks, sampling_rate=130, silent=True)
                rmssd = hrv["HRV_RMSSD"].iloc[0]
                self.CUR_HRV = int(rmssd)
                print(f"HRV_RMSSD: {int(rmssd)} ms; ", end="")
                if rmssd is None:
                    print("undefined")
                elif rmssd < 40:
                    print("You're stressed. Watch out.")
                elif 40 <= rmssd <= 90:
                    print("Normal")
                elif 90 <= rmssd <= 240:
                    print("Excellent, great job!")
                elif rmssd > 240 and len(self.ecg_data_list) < samples_in_minute:
                    print("Okay, the sensor is glitching out. Not giving up hope yet.")
                    self.ecg_data_list.clear()
                elif rmssd > 240:
                    print("Okay, the sensor is glitching out. Giving up hope and resetting...")
                    self.ecg_data_list.clear()
                else:
                    print("undefined")
            else:
                print("Receiving some more ECG data before starting...")

# Example usage:
# polar = Polar()
# ... do other things ...
# polar.close()  # When you want to stop everything

