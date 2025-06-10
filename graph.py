import numpy as np
import neurokit2 as nk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from datetime import datetime
from typing import Tuple, List

def rebuild_ecg_signal(
    file_path: str,
    start_time_str: str,
    end_time_str: str
) -> Tuple[np.ndarray, List[int], List[datetime]]:
    """
    Loads ECG data, filters by date/time range, and rebuilds as a continuous signal.

    Returns:
        all_samples: 1D numpy array of concatenated ECG samples
        segment_starts: List of indices where each segment (row) starts in all_samples
        segment_times: List of datetime objects for each segment
    """
    # Parse datetimes
    start_time = datetime.strptime(start_time_str, '%m/%d/%Y %I:%M:%S %p')
    end_time = datetime.strptime(end_time_str, '%m/%d/%Y %I:%M:%S %p')

    # Load data
    df = pd.read_csv(file_path, header=None)
    df.rename(columns={0: 'datetime'}, inplace=True)
    df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%Y %I:%M:%S %p')

    # Filter by time range
    mask = (df['datetime'] >= start_time) & (df['datetime'] <= end_time)
    filtered_df = df.loc[mask]

    if filtered_df.empty:
        print("No data found in specified time range")
        return np.array([]), [], []

    all_samples = []
    segment_starts = []
    segment_times = []
    for idx, row in filtered_df.iterrows():
        segment_starts.append(len(all_samples))
        samples = row[1:].astype(float).values
        all_samples.extend(samples)
        segment_times.append(row['datetime'])

    return np.array(all_samples), segment_starts, segment_times

def plot_ecg_signal(
    all_samples: np.ndarray,
    segment_starts: List[int],
    segment_times: List[datetime],
    title: str = "ECG Signal",
    show_legend: bool = False
):
    if all_samples.size == 0:
        print("No data to plot.")
        return

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(all_samples, color='b', linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Microvolts (μV)")
    ax.grid(True)

    if show_legend and segment_starts:
        for seg_start in segment_starts:
            ax.axvline(seg_start, color='r', linestyle='--', alpha=0.3)
        ax.legend([dt.strftime('%H:%M:%S') for dt in segment_times], title="Segment Start Times")

    vline = ax.axvline(x=0, color='g', linestyle='--', alpha=0.7, visible=False)
    timestamp_text = ax.text(
        0, 0, '', color='green', fontsize=10,
        verticalalignment='bottom', horizontalalignment='center', visible=False
    )

    def get_timestamp(x):
        segment_index = 0
        for i, start in enumerate(segment_starts):
            if x >= start:
                segment_index = i
            else:
                break
        return segment_times[segment_index].strftime('%Y-%m-%d %I:%M:%S %p')

    def on_mouse_move(event):
        if event.inaxes == ax and toggle_line.get_status()[0]:
            if event.xdata is not None:
                x = int(event.xdata)
                if 0 <= x < len(all_samples):
                    vline.set_xdata(x)
                    vline.set_visible(True)
                    timestamp_text.set_text(get_timestamp(x))
                    timestamp_text.set_x(x)
                    # Place timestamp 5% above the bottom of the current y-limits
                    ylim = ax.get_ylim()
                    y_pos = ylim[0] + 0.05 * (ylim[1] - ylim[0])
                    timestamp_text.set_y(y_pos)
                    timestamp_text.set_visible(True)
                    fig.canvas.draw_idle()
        else:
            vline.set_visible(False)
            timestamp_text.set_visible(False)
            fig.canvas.draw_idle()

    rax = plt.axes([0.01, 0.7, 0.1, 0.15])
    toggle_line = CheckButtons(rax, ['Show Timestamp Line'], [False])

    fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

    plt.tight_layout()
    plt.show()




# Example usage:
if __name__ == "__main__":
    file_path = "ecg_log.txt"
    start_time = "06/09/2025 07:40:50 PM"
    end_time = "06/09/2025 08:25:58 PM"

    # Step 1: Rebuild the signal
    ecg_signal, seg_starts, seg_times = rebuild_ecg_signal(file_path, start_time, end_time)

    print(list(ecg_signal))
    print(seg_starts)
    print(seg_times)
    print(len(seg_starts))
    print(len(seg_times))

    # Step 2: Plot the signal
    plot_ecg_signal(
        ecg_signal,
        seg_starts,
        seg_times,
        title=f"ECG from {start_time} to {end_time}",
        show_legend=False  # Set True for segment markers/legend
    )
