import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from tor.base import DBManager

class RollWarnings:
    def __init__(self):
        self.fig, ax = plt.subplots(figsize=(5, 15)) # ax is a placeholder here
        self.canvas = FigureCanvas(self.fig)
        ax.text(0.5, 0.5, 'No data loaded yet.', ha='center', va='center') # Initial message

    def loadData(self, start, end):
        query = """
            SELECT 
                l.ClientId, 
                c.Position, 
                c.Latin, 
                c.Material, 
                CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(l.Message, '[', -1), ',', 1) AS DECIMAL(10,2)) AS XPos 
            FROM 
                clientlog l 
            LEFT JOIN 
                client c ON c.Id = l.ClientId 
            WHERE
                Time >= %(start)s
                AND Time <= %(end)s
                AND MessageType = 'WARNING'
                AND MessageCode = 'NO_MAGNET_CONTACT'
        """
        warnings = DBManager.executeQuery(query, {"start": start, "end": end})
        clientsRaw = DBManager.getAllPossibleClients()
        allData = {c.Id: {"label": c.Material, "values": []} for c in clientsRaw}
        for w in warnings:
            if w.ClientId in allData:
                allData[w.ClientId]["values"].append(float(w.XPos))

        plot_data = {k: v for k, v in allData.items() if v['values']}

        return plot_data



    def updatePlot(self, start, end):
        print(f"Fetching data from '{start}' to '{end}'...")
        plot_data = self.loadData(start, end)

        labels = [client['label'] for client in plot_data.values()]
        values = [client['values'] for client in plot_data.values()]

        self.fig.clf()
        axes = self.fig.subplots(nrows=len(plot_data))
        # If there's only one subplot, make sure it's iterable
        if len(plot_data) == 1:
            axes = [axes]

        min_val = 55
        max_val = 195
        num_bins = 25
        bins = np.linspace(min_val, max_val, num_bins + 1)
        all_values = [item for sublist in values for item in sublist]
        vmin = min(all_values)
        vmax = max(all_values)

        histograms = []
        bin_edges = []
        for v in values:
            h, e =np.histogram(v, bins=bins)
            histograms.append(h)
            bin_edges.append(e)

        vmin = 0
        vmax = max([h.max() for h in histograms])

        im = None  # Initialize im to ensure it's available for the colorbar
        for i, (ax, label, counts, edges) in enumerate(zip(axes, labels, histograms, bin_edges)):
            heatmap_data = counts.reshape(1, -1)

            # Create a custom colormap to handle empty bins as white
            # We will use viridis for non-zero values and prepend white for the value 0
            viridis_colors = plt.cm.get_cmap('YlOrRd', 256)(np.arange(256))
            white_color = np.array([1, 1, 1, 1])  # RGBA for white
            # Insert white at the beginning of the colormap
            custom_cmap_colors = np.vstack([white_color, viridis_colors])
            custom_cmap = mcolors.ListedColormap(custom_cmap_colors)

            im = ax.imshow(heatmap_data, cmap=custom_cmap, aspect='auto', vmin=vmin, vmax=vmax)

            if i == len(axes) - 1:
                bin_centers = (edges[:-1] + edges[1:]) / 2
                ax.set_xticks(np.arange(len(bin_centers)))
                ax.set_xticklabels([f'{int(edges[i])}-{int(edges[i + 1])}' for i in range(len(edges) - 1)],
                                   rotation=45, ha='right')
            else:
                ax.set_xticks([])

            ax.set_yticks([0])
            ax.set_yticklabels([label])

        cb = self.fig.colorbar(im, ax=axes, label='Frequency (Count)')
        cb.set_ticks(np.arange(0, vmax + 1))
        self.fig.suptitle('Roll Problems')

        self.fig.tight_layout(rect=[0, 0, 0.7, 1])

        # 5. Redraw the canvas to display the new plot in your application.
        self.canvas.draw()

