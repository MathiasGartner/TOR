import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import pandas as pd

from tor.base import DBManager

class ResultPositions:
    def __init__(self):
        self.fig, ax = plt.subplots(figsize=(5, 15)) # ax is a placeholder here
        self.canvas = FigureCanvas(self.fig)
        ax.text(0.5, 0.5, 'No data loaded yet.', ha='center', va='center') # Initial message
        self.cbar = None

    def loadData(self, start, end, event):
        resultsRaw = []
        if event is not None and start is not None and end is not None:
            resultsRaw = DBManager.getResultsByDatenAndEvent(start, end, event)
        elif event is not None:
            resultsRaw = DBManager.getResultsByEvent(event)
        elif start is not None and end is not None:
            resultsRaw = DBManager.getResultsByDate(start, end)

        columns = ["Position", "Latin", "X", "Y"]
        col_idx = [0, 1, 4, 5]
        results = [[r[col] for col in col_idx] for r in resultsRaw]
        df = pd.DataFrame(results, columns=columns)
        return df

    def updatePlot(self, start, end, event, globalColorBar):
        print(f"Fetching data from '{start}' to '{end}' for event {event}...")
        df = self.loadData(start, end, event)

        bins = (20, 10)

        df_sorted = df.drop_duplicates(subset=["Latin"]).sort_values("Position")
        clients = df_sorted["Latin"].values
        positions = df_sorted["Position"].values
        n_clients = len(clients)

        # Fixed axis range
        x_range = [0, 1]
        y_range = [0, 1]

        # First pass: compute global density max
        global_max = 0
        local_maxes = []
        for client in clients:
            client_data = df[df["Latin"] == client]
            H, _, _ = np.histogram2d(client_data["X"], client_data["Y"], bins=bins, range=[x_range, y_range])
            global_max = max(global_max, H.max())
            local_maxes.append(H.max() if H.max() > 0 else 1)

        # subplot grid
        n_rows = 5
        n_cols = 6
        if hasattr(self, "cbar") and self.cbar is not None:
            try:
                self.cbar.remove()
            except:
                pass
            self.cbar = None
        self.fig.clf()
        axes = self.fig.subplots(n_rows, n_cols)
        axes = axes.flatten()

        # color map
        viridis_colors = plt.cm.get_cmap('YlOrRd', 256)(np.arange(256))
        white_color = np.array([1, 1, 1, 1])  # RGBA for white
        # Insert white at the beginning of the colormap
        custom_cmap_colors = np.vstack([white_color, viridis_colors])
        custom_cmap = mcolors.ListedColormap(custom_cmap_colors)
        custom_cmap = "YlOrRd"

        # Plot per client
        for ax, client, pos, local_max in zip(axes, clients, positions, local_maxes):
            client_data = df[df["Latin"] == client]
            h = ax.hist2d(client_data["X"], client_data["Y"], bins=bins, cmap=custom_cmap, range=[x_range, y_range], vmin=0, vmax=(global_max if globalColorBar else local_max))
            ax.set_title(f"#{'--' if math.isnan(pos) else int(pos)}: {client} ({len(client_data)})", fontsize=7)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel("Ramp", fontsize=4)
            ax.set_ylabel("")
            ax.set_aspect(0.5)
            if not globalColorBar:
                cax = inset_axes(ax,
                                 width="5%",  # relative to subplot width
                                 height="100%",  # relative to subplot height (plot area only)
                                 loc="lower left",
                                 bbox_to_anchor=(1.05, 0, 1, 1),
                                 bbox_transform=ax.transAxes,
                                 borderpad=0)
                cb = self.fig.colorbar(h[3], cax=cax)
                cb.ax.tick_params(labelsize=5)

        # Remove empty subplots if any
        for ax in axes[len(clients):]:
            ax.axis("off")
        self.fig.patch.set_visible(False)

        # One global colorbar
        if globalColorBar:
            self.cbar = self.fig.colorbar(
                h[3], ax=axes,
                label=f"# of Results (total {len(df)})",
                shrink=0.9
            )

        #self.fig.tight_layout(rect=[0, 0, 0.7, 1])
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.5, hspace=0.3)

        # 5. Redraw the canvas to display the new plot in your application.
        self.canvas.draw()


