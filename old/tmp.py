import asyncio
import signal
import threading
from typing import Union
from bleak import BleakScanner
from rich.console import Console
from rich import inspect
import numpy as np
import matplotlib.pyplot as plt
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

exit_event = threading.Event()


def handle_exit(signum, frame):
    console.print("[bold red]Received exit signal[/bold red]")
    exit_event.set()


ecg_data_list = []


def heartrate_callback(data: HRData):
    print(f"Heart Rate: {int(data.heartrate)}")
    pass


def data_callback(data: Union[ECGData, ACCData]):
    #console.print(f"[bold green]Received Data:[/bold green] {data}")
    if isinstance(data, ECGData):
        ecg_data_list.extend(data.data)

        if len(ecg_data_list) > 2500:
            # Calculate the sample index for the start of the last minute
            samples_in_minute = 60 * 130  # 60 seconds * 130 hz = 7800 samples
            cut = samples_in_minute * 1
            start_index = int(max(0, len(ecg_data_list) - cut))

            peaks, info = nk.ecg_peaks(ecg_data_list[start_index:], sampling_rate=130)


        # --- Begin MAD Filter Addition ---
            # Calculate RR intervals (in ms)
            rpeaks = np.where(peaks == 1)[0]
            rr_intervals = np.diff(rpeaks) / 130 * 1000  # ms

            # MAD filter function
            def mad_filter(rr, threshold=3.5, window=11):
                rr_series = pd.Series(rr)
                rolling_median = rr_series.rolling(window, center=True, min_periods=1).median()
                mad = (rr_series - rolling_median).abs().rolling(window, center=True, min_periods=1).median()
                outliers = ((rr_series - rolling_median).abs() > threshold * mad)
                rr_filtered = rr_series.copy()
                rr_filtered[outliers] = rolling_median[outliers]
                return rr_filtered.values

            rr_filtered = mad_filter(rr_intervals)

            # Reconstruct filtered peaks array
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
            print(f"HRV_RMSSD: {int(rmssd)} ms; ", end="")
            if rmssd is None:
                print("undefined")
            elif rmssd < 40:
                print("You're stressed. Watch out.")
            elif 40 <= rmssd <= 90:
                print("Normal")
            elif 90 <= rmssd <= 240:
                print("Excellent, great job!")
            elif rmssd > 240 and len(ecg_data_list) < samples_in_minute:
                print("Okay, the sensor is glitching out. Not giving up hope yet.")
                ecg_data_list.clear()
            elif rmssd > 240:
                print("Okay, the sensor is glitching out. Giving up hope and resetting...")
                ecg_data_list.clear()

            else:
                print("undefined")
        else:
            print("Receiving some more ECG data before starting...")

async def main():
    device = await BleakScanner.find_device_by_filter(
        lambda bd, ad: bd.name and "Polar H10" in bd.name, timeout=5
    )
    if device is None:
        console.print("[bold red]Device not found[/bold red]")
        return

    inspect(device)

    async with PolarDevice(device) as polar_device:
        available_features = await polar_device.available_features()
        inspect(available_features)

        for feature in available_features:
            settings = await polar_device.request_stream_settings(feature)
            console.print(f"[bold blue]Settings for {feature}:[/bold blue] {settings}")

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

        polar_device.set_callback(data_callback, heartrate_callback)

        await polar_device.start_stream(ecg_settings)
        await polar_device.start_stream(acc_settings)

        await polar_device.start_heartrate_stream()

        while not exit_event.is_set():
            await asyncio.sleep(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
        console.print("[bold red]Program exited gracefully[/bold red]")


