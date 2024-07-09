from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyleOption, QStyle
from PySide6.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

from gecho.geometry.geometry import Geometry


def color_gen():
    while True:
        colors = ["#4bb4ff",
                  "#4bffb4",
                  "#ff4bb4"]
        for c in colors:
            yield c


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.label = QLabel("Preview")
        self.label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.label)

        self.figure = Figure()
        self.figure.set_facecolor("#0D1013")
        self.figure.tight_layout()

        self.ax = self.figure.add_subplot()

        self.ax.set_facecolor("#0D1013")
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('white')  # Set border color
            spine.set_linewidth(1)

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas)

        layout.setContentsMargins(10, 10, 10, 10)

        self.colors = None

        self.setLayout(layout)

    def plot_layer(self, layer: Geometry.Layer):
        z = np.concatenate([layer.bot.zs, layer.top.zs[::-1], [layer.bot.zs[0]]])
        r = np.concatenate([layer.bot.rs, layer.top.rs[::-1], [layer.bot.rs[0]]])

        c = next(self.colors)

        self.ax.fill(z, r, c=c, label=layer.name)
        self.ax.scatter(z, r, c="white", linestyle="-", linewidth=1)

        ref = True

        if ref:
            self.ax.fill(z, -r, c=c)
            self.ax.plot(z, -r, c="white", linestyle="-", linewidth=1)

    def plot_geometry(self, geometry: Geometry):
        self.colors = color_gen()

        self.ax.clear()

        for layer in geometry.layers:
            self.plot_layer(layer)

        x = np.array(geometry.wall.bot.zs)
        y = np.array(geometry.wall.bot.rs)

        self.ax.plot(x, y, "r.", label=geometry.wall.name)
        self.ax.plot(x, -y, "r")

        # for mon in chamber.monitors:
        #     if mon.type == "s":
        #         plot(mon.z, mon.r, "s-Monitor", c1="magenta", c2="magenta", alpha=0.5, linestyle="-", ref=False)
        #     if mon.type == "z":
        #         zmon = mon
        #         plot(mon.z, mon.r, "z-Monitor", c1="lime", c2="lime", alpha=0.5, linestyle="-", ref=False)

        # plt.title("Geometry")

        self.ax.legend()
        self.ax.set_ylabel("r-axis (m)", color="white")
        self.ax.set_xlabel("z-axis (m)", color="white")

        self.canvas.draw()

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, o, p, self)
