from PySide6.QtWidgets import QMainWindow, QMenu, QMenuBar, QVBoxLayout, QWidget, QScrollArea, QPushButton, \
    QSplitter
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from .plot_widget import PlotWidget
from .layer_widget import LayerWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Geometry Project")

        # Set up the menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)

        open_project_action = QAction("Open Project", self)
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)

        # Set up the main layout
        self.main_layout = QVBoxLayout()

        self.splitter = QSplitter(Qt.Vertical)

        self.layers_widget = QWidget()
        self.layers_layout = QVBoxLayout()
        self.layers_widget.setLayout(self.layers_layout)

        self.add_layer_button = QPushButton("+")
        self.add_layer_button.clicked.connect(self.add_layer)
        self.layers_layout.addWidget(self.add_layer_button)

        self.layer_area = QScrollArea()
        self.layer_area.setWidgetResizable(True)
        self.layer_list_widget = QWidget()
        self.layer_list_layout = QVBoxLayout()
        self.layer_list_widget.setLayout(self.layer_list_layout)
        self.layer_area.setWidget(self.layer_list_widget)

        self.layers_layout.addWidget(self.layer_area)

        self.plot_widget = PlotWidget()

        self.splitter.addWidget(self.layers_widget)
        self.splitter.addWidget(self.plot_widget)

        self.main_layout.addWidget(self.splitter)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def open_project(self):
        # Implementation to open a project file
        pass

    def add_layer(self):
        layer_widget = LayerWidget(self.layer_list_layout)
        layer_widget.parameters_changed.connect(self.update_plot)
        self.layer_list_layout.addWidget(layer_widget)

    def update_plot(self):
        x = range(-10, 11)  # example range from -10 to 10
        self.plot_widget.figure.clear()
        ax = self.plot_widget.figure.add_subplot(111)

        for i in range(self.layer_list_layout.count()):
            layer_widget = self.layer_list_layout.itemAt(i).widget()
            if layer_widget:
                slope, intercept = layer_widget.get_parameters()
                y = [slope * xi + intercept for xi in x]
                ax.plot(x, y, label=f"y={slope}x+{intercept}")

        ax.legend()
        self.plot_widget.canvas.draw()
