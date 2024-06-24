from PySide6 import QtGui
from PySide6.QtWidgets import QMainWindow, QMenu, QMenuBar, QVBoxLayout, QWidget, QScrollArea, QPushButton, \
    QSplitter, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from .plot_widget import PlotWidget
from .layer_widget import LayerWidget
from .layer_details_widget import LayerDetailsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Geometry Project")
        self.setGeometry(100, 100, 1600, 800)

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

        self.vertical_splitter = QSplitter(Qt.Vertical)

        self.top_splitter = QSplitter(Qt.Horizontal)

        self.layers_widget = QWidget()
        # self.layers_widget.setMinimumWidth(300)
        # self.layers_widget.setMaximumWidth(300)
        # self.layers_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.layers_layout = QVBoxLayout()
        self.layers_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layers_widget.setLayout(self.layers_layout)

        self.layers_layout.addWidget(QLabel("Components"))

        self.component_buttons_layout = QHBoxLayout()

        self.add_element_button = QPushButton("Add Element")
        self.add_element_button.setIcon(QIcon("resources/icons/element.png"))
        self.add_element_button.clicked.connect(self.add_element)
        self.component_buttons_layout.addWidget(self.add_element_button)

        self.add_monitor_button = QPushButton("Add Monitor")
        self.add_monitor_button.setIcon(QIcon("resources/icons/monitor.png"))
        self.add_monitor_button.clicked.connect(self.add_monitor)
        self.component_buttons_layout.addWidget(self.add_monitor_button)

        self.layers_layout.addLayout(self.component_buttons_layout)

        self.layer_area = QScrollArea()
        self.layer_area.setWidgetResizable(True)
        self.layer_list_widget = QWidget()
        self.layer_list_widget.setContentsMargins(0, 0, 0, 0)
        self.layer_list_layout = QVBoxLayout()
        self.layer_list_layout.setContentsMargins(0, 3, 0, 3)
        self.layer_list_layout.setSpacing(0)
        self.layer_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Top-align the layers
        self.layer_list_widget.setLayout(self.layer_list_layout)
        self.layer_area.setWidget(self.layer_list_widget)

        self.layers_layout.addWidget(self.layer_area)

        self.layer_details_widget = LayerDetailsWidget()
        # self.layer_details_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self.layer_details_widget.parameters_changed.connect(self.update_plot)

        self.top_splitter.addWidget(self.layers_widget)
        self.top_splitter.addWidget(self.layer_details_widget)

        self.top_splitter.setStretchFactor(0, 1)
        self.top_splitter.setStretchFactor(1, 6)

        self.plot_widget = PlotWidget()
        self.plot_widget.setMinimumHeight(100)

        self.vertical_splitter.addWidget(self.top_splitter)
        self.vertical_splitter.addWidget(self.plot_widget)

        self.vertical_splitter.setStretchFactor(0, 5)
        self.vertical_splitter.setStretchFactor(1, 1)

        self.main_layout.addWidget(self.vertical_splitter)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.selected_layer = None

    def open_project(self):
        # Implementation to open a project file
        pass

    def add_element(self):
        layer_widget = LayerWidget(self.layer_list_layout, "element")
        layer_widget.selected.connect(lambda: self.display_layer_details(layer_widget))
        layer_widget.deselect_all.connect(self.deselect_all_layers)
        self.layer_list_layout.addWidget(layer_widget)

    def add_monitor(self):
        layer_widget = LayerWidget(self.layer_list_layout, "monitor")
        layer_widget.selected.connect(lambda: self.display_layer_details(layer_widget))
        layer_widget.deselect_all.connect(self.deselect_all_layers)
        self.layer_list_layout.addWidget(layer_widget)

    def display_layer_details(self, layer_widget):
        self.selected_layer = layer_widget
        slope, intercept = self.layer_details_widget.get_parameters()
        self.layer_details_widget.set_parameters(slope, intercept)

    def deselect_all_layers(self):
        for i in range(self.layer_list_layout.count()):
            layer_widget = self.layer_list_layout.itemAt(i).widget()
            if layer_widget:
                layer_widget.deselect_layer()

    def update_plot(self):
        x = range(-10, 11)  # example range from -10 to 10
        self.plot_widget.figure.clear()
        ax = self.plot_widget.figure.add_subplot(111)

        for i in range(self.layer_list_layout.count()):
            layer_widget = self.layer_list_layout.itemAt(i).widget()
            if layer_widget:
                slope, intercept = self.layer_details_widget.get_parameters()
                y = [slope * xi + intercept for xi in x]
                ax.plot(x, y, label=f"y={slope}x+{intercept}")

        ax.legend()
        self.plot_widget.canvas.draw()


'''
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
        self.layer_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
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
'''