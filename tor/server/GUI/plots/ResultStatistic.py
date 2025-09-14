import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pandas as pd

from tor.base import DBManager

class ResultStatistic:
    def __init__(self):
        self.fig, ax = plt.subplots(figsize=(5, 15)) # ax is a placeholder here
        self.canvas = FigureCanvas(self.fig)
        ax.text(0.5, 0.5, 'No data loaded yet.', ha='center', va='center') # Initial message

    def loadData(self, start, end, event):
        resultsRaw = []
        if event is not None and start is not None and end is not None:
            resultsRaw = DBManager.getResultsByDatenAndEvent(start, end, event)
        elif event is not None:
            resultsRaw = DBManager.getResultsByEvent(event)
        elif start is not None and end is not None:
            resultsRaw = DBManager.getResultsByDate(start, end)

        columns = ["Position", "Latin", "Time"]
        col_idx = [0, 1, 6]
        results = [[r[col] for col in col_idx] for r in resultsRaw]
        df = pd.DataFrame(results, columns=columns)
        return df

    def updatePlot(self, start, end, event):
        print(f"Fetching data from '{start}' to '{end}' for event {event}...")
        df = self.loadData(start, end, event)

        num_bins = 400

        # Sort by position and get unique Latin names
        df_sorted = df.drop_duplicates(subset=["Latin"]).sort_values("Position")
        latin_order = df_sorted["Latin"].values

        # Convert time to numeric (for histogram)
        time_numeric = df["Time"].astype(np.int64)  # nanoseconds since epoch

        # Create 200 bins between min and max
        time_bins = np.linspace(time_numeric.min(), time_numeric.max(), num_bins + 1)

        # Create heatmap data
        heatmap_data = np.zeros((len(latin_order), len(time_bins) - 1))

        for i, latin in enumerate(latin_order):
            times = df[df["Latin"] == latin]["Time"]
            counts, _ = np.histogram(times.astype(np.int64), bins=time_bins.astype(np.int64))
            heatmap_data[i, :] = counts

        # Plot heatmap
        self.fig.clf()
        axes = self.fig.subplots()
        im = axes.imshow(heatmap_data, aspect='auto', cmap="YlOrRd", origin="lower")

        # Set y-axis ticks
        axes.set_yticks(np.arange(len(latin_order)))
        axes.set_yticklabels(latin_order)

        # x-axis ticks: convert numeric back to datetime
        time_bin_dates = pd.to_datetime(time_bins[:-1])
        num_xticks = 10  # how many ticks to show
        xticks_idx = np.linspace(0, 199, num_xticks, dtype=int)
        axes.set_xticks(xticks_idx)
        axes.set_xticklabels(time_bin_dates[xticks_idx].strftime("%Y-%m-%d %H:%M"), rotation=45, ha='right')

        axes.set_xlabel("Time")
        axes.set_ylabel("Latin Name")
        axes.set_title("Result Heatmap")

        # Colorbar
        cbar = self.fig.colorbar(im, ax=axes)
        cbar.set_label("Number of Result")

        self.canvas.draw()