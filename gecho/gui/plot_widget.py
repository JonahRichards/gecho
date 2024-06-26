from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyleOption, QStyle
from PySide6.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas)

        layout.setContentsMargins(10, 10, 10, 10)

        self.ax = self.figure.add_subplot()

        self.setLayout(layout)

        self.plot_data([1], [1])

    def plot_data(self, x, y):
        self.ax.clear()
        self.ax.plot(x, y)
        self.canvas.draw()

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, o, p, self)
