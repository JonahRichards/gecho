import os
import pickle

from PySide6 import QtGui
from PySide6.QtWidgets import QMainWindow, QMenu, QMenuBar, QVBoxLayout, QWidget, QScrollArea, QPushButton, \
    QSplitter, QLabel, QHBoxLayout, QSizePolicy, QTreeWidget, QFrame, QDialog, QGridLayout, QLineEdit, QFileDialog, \
    QMessageBox, QTreeWidgetItem, QTabWidget
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from .plot_widget import PlotWidget
from .layer_widget import LayerWidget
from .layer_details_widget import LayerDetailsWidget

from gecho.gui.project_manager import ProjectManager
from gecho.geometry.geometry import Geometry

ICON_MAP = {".npy": "3d-array.png",
            ".geom": "geometry.png",
            ".tif": "image.png",
            ".tiff": "image.png",
            ".jpg": "image.png",
            ".png": "image.png"}


class MainWindow(QMainWindow):
    def __init__(self, root):
        super().__init__()
        self.setWindowTitle("GECHO-alphav0.1")
        self.setGeometry(300, 300, 1600, 800)
        self.root = root

        # PROJECT MANAGER
        self.project_manager = ProjectManager(root)

        # MENU BAR
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)

        new_action = QAction(QIcon('resources/icons/new.png'), "New Project", self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction(QIcon('resources/icons/open.png'), "Open Project", self)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        # MAIN LAYOUT
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)

        self.top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.vertical_splitter.addWidget(self.top_splitter)

        # PROJECT FILES
        left_panel = QFrame(self.top_splitter)
        self.left_panel_layout = QVBoxLayout(left_panel)

        project_files_label = QLabel("Project Files")
        self.left_panel_layout.addWidget(project_files_label)

        self.project_buttons_layout = QHBoxLayout()
        self.left_panel_layout.addLayout(self.project_buttons_layout)

        self.add_geometry_button = QPushButton(" New Geometry")
        self.add_geometry_button.setIcon(QIcon("resources/icons/geometry.png"))
        self.add_geometry_button.clicked.connect(self.new_geometry)
        self.project_buttons_layout.addWidget(self.add_geometry_button)

        self.project_list_widget = QTreeWidget()
        self.project_list_widget.setHeaderHidden(True)
        self.project_list_widget.itemSelectionChanged.connect(self.on_project_list_item_selected)
        self.project_list_widget.itemExpanded.connect(self.on_item_expanded)
        self.project_list_widget.itemCollapsed.connect(self.on_item_collapsed)
        self.project_list_widget.setIconSize(QSize(20, 20))

        self.left_panel_layout.addWidget(self.project_list_widget)

        self.tabs = QTabWidget()
        self.top_splitter.addWidget(self.tabs)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.construct()
        self.simulate()
        self.analyze()

        self.top_splitter.setStretchFactor(0, 1)
        self.top_splitter.setStretchFactor(1, 3)

        # PLOTTER
        self.plot_widget = PlotWidget()
        self.plot_widget.setMinimumHeight(100)
        self.vertical_splitter.addWidget(self.plot_widget)

        self.vertical_splitter.setStretchFactor(0, 2)
        self.vertical_splitter.setStretchFactor(1, 1)

        self.main_layout.addWidget(self.vertical_splitter)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.project_manager.open_project('C:/Projects/gecho/data/test')
        self.update_project_list()

    def construct(self):
        # LAYERS PANEL
        right_panel = QFrame(self.tabs)
        self.right_panel_layout = QHBoxLayout(right_panel)
        self.right_panel_layout.setContentsMargins(0, 0, 0, 0)

        self.layers_panel = QFrame(right_panel)
        self.layers_panel.setContentsMargins(0, 0, 0, 0)
        self.layers_panel.setFixedWidth(270)
        self.right_panel_layout.addWidget(self.layers_panel)

        self.layers_layout = QVBoxLayout(self.layers_panel)
        self.layers_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.layers_labels_layout = QHBoxLayout()
        self.layers_layout.addLayout(self.layers_labels_layout)

        # self.layers_labels_layout.addWidget(QLabel("Geometry:"))
        self.layers_file_name_label = QLabel("")
        # self.layers_file_name_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layers_labels_layout.addWidget(self.layers_file_name_label)

        # LAYER BUTTONS
        self.component_buttons_layout = QHBoxLayout()
        self.layers_layout.addLayout(self.component_buttons_layout)

        self.add_layer_button = QPushButton(" Add Layer")
        self.add_layer_button.setIcon(QIcon("resources/icons/layer.png"))
        self.add_layer_button.clicked.connect(self.add_layer)
        self.component_buttons_layout.addWidget(self.add_layer_button)

        # self.add_monitor_button = QPushButton(" Add Monitor")
        # self.add_monitor_button.setIcon(QIcon("resources/icons/monitor.png"))
        # self.add_monitor_button.clicked.connect(self.add_monitor)
        # self.component_buttons_layout.addWidget(self.add_monitor_button)

        # LAYER LIST
        self.layer_area = QScrollArea()
        self.layer_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.layer_area.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.layer_area.setWidgetResizable(True)
        self.layers_layout.addWidget(self.layer_area)

        self.layer_list_widget = QWidget()
        self.layer_list_widget.setContentsMargins(0, 0, 0, 0)

        self.layer_list_layout = QVBoxLayout()
        self.layer_list_layout.setContentsMargins(0, 3, 0, 3)
        self.layer_list_layout.setSpacing(0)
        self.layer_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Top-align the layers
        self.layer_list_widget.setLayout(self.layer_list_layout)
        self.layer_area.setWidget(self.layer_list_widget)

        # LAYER PROPERTIES
        self.layer_properties_layout = QVBoxLayout()
        self.right_panel_layout.addLayout(self.layer_properties_layout)
        self.layer_properties_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.layer_properties_layout.addWidget(QLabel(""))

        self.layer_details_widget = LayerDetailsWidget()
        self.layer_details_widget.parameters_changed.connect(self.update_plot)
        self.layer_details_widget.info_changed.connect(self.update_construct_names)
        self.layer_details_widget.delete_layer.connect(self.delete_layer)

        self.layer_properties_layout.addWidget(self.layer_details_widget)

        self.tabs.addTab(right_panel, " Construct ")

    def update_construct(self):
        self.layers_file_name_label.setText(self.project_manager.current_item_path.split("/")[-1])

        while self.layer_list_layout.count():
            item = self.layer_list_layout.takeAt(0)
            if item is not None:
                item.widget().deleteLater()
            else:
                break

        if self.project_manager.current_item_path.endswith(".geom"):
            self.add_layer_button.setDisabled(False)
            self.layers_file_name_label.setStyleSheet("QLabel {color: #ffffff}")

            layer_widget = LayerWidget(self.project_manager.current_item.wall)
            layer_widget.selected.connect(self.display_layer_details)
            layer_widget.deselect_all.connect(self.deselect_all_layers)
            self.layer_list_layout.addWidget(layer_widget)
            layer_widget.mousePressEvent(Qt.MouseEventFlag.MouseEventCreatedDoubleClick)

            for i, layer in enumerate(self.project_manager.current_item.layers):
                layer_widget = LayerWidget(layer)
                layer_widget.selected.connect(self.display_layer_details)
                layer_widget.deselect_all.connect(self.deselect_all_layers)
                self.layer_list_layout.addWidget(layer_widget)
        else:
            self.add_layer_button.setDisabled(True)
            self.layers_file_name_label.setStyleSheet("QLabel {color: #777a7e}")
            self.layer_details_widget.layer = None

        self.layer_details_widget.update_properties()

    def update_construct_names(self):
        wall = self.layer_list_layout.itemAt(0)
        wall.widget().label.setText(self.project_manager.current_item.wall.name)

        for i in range(1, self.layer_list_layout.count()):
            item = self.layer_list_layout.itemAt(i)
            item.widget().label.setText(self.project_manager.current_item.layers[i-1].name)

        self.project_manager.current_item.save()

    def delete_layer(self, layer):
        self.project_manager.current_item.layers.remove(layer)
        self.project_manager.current_item.save()
        self.update_construct()

    def simulate(self):
        # LAYERS PANEL
        right_panel = QFrame(self.tabs)
        self.tabs.addTab(right_panel, " Simulate ")
        self.right_panel_layout = QHBoxLayout(right_panel)
        self.right_panel_layout.setContentsMargins(0, 0, 0, 0)

        # self.layers_panel = QFrame(right_panel)
        # self.layers_panel.setContentsMargins(0, 0, 0, 0)
        # self.layers_panel.setFixedWidth(270)
        # self.right_panel_layout.addWidget(self.layers_panel)
        #
        # self.layers_layout = QVBoxLayout(self.layers_panel)
        # self.layers_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        #
        # self.layers_layout.addWidget(QLabel("Components"))
        #
        # # LAYER BUTTONS
        # self.component_buttons_layout = QHBoxLayout()
        # self.layers_layout.addLayout(self.component_buttons_layout)
        #
        # self.add_element_button = QPushButton(" Add Element")
        # self.add_element_button.setIcon(QIcon("resources/icons/element.png"))
        # self.add_element_button.clicked.connect(self.add_element)
        # self.component_buttons_layout.addWidget(self.add_element_button)
        #
        # # self.add_monitor_button = QPushButton(" Add Monitor")
        # # self.add_monitor_button.setIcon(QIcon("resources/icons/monitor.png"))
        # # self.add_monitor_button.clicked.connect(self.add_monitor)
        # # self.component_buttons_layout.addWidget(self.add_monitor_button)
        #
        # # LAYER LIST
        # self.layer_area = QScrollArea()
        # self.layer_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # # self.layer_area.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        # self.layer_area.setWidgetResizable(True)
        # self.layers_layout.addWidget(self.layer_area)
        #
        # self.layer_list_widget = QWidget()
        # self.layer_list_widget.setContentsMargins(0, 0, 0, 0)
        #
        # self.layer_list_layout = QVBoxLayout()
        # self.layer_list_layout.setContentsMargins(0, 3, 0, 3)
        # self.layer_list_layout.setSpacing(0)
        # self.layer_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Top-align the layers
        # self.layer_list_widget.setLayout(self.layer_list_layout)
        # self.layer_area.setWidget(self.layer_list_widget)
        #
        # # LAYER PROPERTIES
        # self.layer_details_widget = LayerDetailsWidget()
        # self.layer_details_widget.parameters_changed.connect(self.update_plot)
        # self.right_panel_layout.addWidget(self.layer_details_widget)

    def analyze(self):
        # LAYERS PANEL
        right_panel = QFrame(self.tabs)
        self.tabs.addTab(right_panel, " Analyze ")
        # self.right_panel_layout = QHBoxLayout(right_panel)
        # self.right_panel_layout.setContentsMargins(0, 0, 0, 0)
        #
        # self.layers_panel = QFrame(right_panel)
        # self.layers_panel.setContentsMargins(0, 0, 0, 0)
        # self.layers_panel.setFixedWidth(270)
        # self.right_panel_layout.addWidget(self.layers_panel)
        #
        # self.layers_layout = QVBoxLayout(self.layers_panel)
        # self.layers_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        #
        # self.layers_layout.addWidget(QLabel("Components"))
        #
        # # LAYER BUTTONS
        # self.component_buttons_layout = QHBoxLayout()
        # self.layers_layout.addLayout(self.component_buttons_layout)
        #
        # self.add_element_button = QPushButton(" Add Element")
        # self.add_element_button.setIcon(QIcon("resources/icons/element.png"))
        # self.add_element_button.clicked.connect(self.add_element)
        # self.component_buttons_layout.addWidget(self.add_element_button)
        #
        # # self.add_monitor_button = QPushButton(" Add Monitor")
        # # self.add_monitor_button.setIcon(QIcon("resources/icons/monitor.png"))
        # # self.add_monitor_button.clicked.connect(self.add_monitor)
        # # self.component_buttons_layout.addWidget(self.add_monitor_button)
        #
        # # LAYER LIST
        # self.layer_area = QScrollArea()
        # self.layer_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # # self.layer_area.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        # self.layer_area.setWidgetResizable(True)
        # self.layers_layout.addWidget(self.layer_area)
        #
        # self.layer_list_widget = QWidget()
        # self.layer_list_widget.setContentsMargins(0, 0, 0, 0)
        #
        # self.layer_list_layout = QVBoxLayout()
        # self.layer_list_layout.setContentsMargins(0, 3, 0, 3)
        # self.layer_list_layout.setSpacing(0)
        # self.layer_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Top-align the layers
        # self.layer_list_widget.setLayout(self.layer_list_layout)
        # self.layer_area.setWidget(self.layer_list_widget)
        #
        # # LAYER PROPERTIES
        # self.layer_details_widget = LayerDetailsWidget()
        # self.layer_details_widget.parameters_changed.connect(self.update_plot)
        # self.right_panel_layout.addWidget(self.layer_details_widget)

    def on_tab_changed(self, index):
        self.project_manager.current_tab = index
        match index:
            case 0:
                self.update_construct()

    def get_new_name(self, directory, name, ext=None):
        def num():
            for i, _ in enumerate(iter(int, 1)):
                yield str(i + 1)

        new_name = name + ext if ext is not None else name

        if not os.path.exists(directory + new_name):
            return new_name
        else:
            nums = num()
            while True:
                new_name = name + next(nums)
                new_name += ext if ext is not None else ""
                if not os.path.exists(directory + new_name):
                    return new_name

    def new_geometry(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Geometry")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        name_label = QLabel("Name:")
        grid_layout.addWidget(name_label, 0, 0)

        self.geometry_name_line_edit = QLineEdit()
        self.geometry_name_line_edit.setText("New Geometry")
        grid_layout.addWidget(self.geometry_name_line_edit, 0, 1)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(lambda: self.create_geometry(dialog))
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        dialog.exec_()

    def create_geometry(self, dialog):
        directory = self.project_manager.project_dir
        name = self.geometry_name_line_edit.text()

        if not name:
            QMessageBox.warning(self, "Invalid Input", "Must provide geometry filename.")
            return

        if name.endswith(".geom"):
            name = name[:-5]

        name = self.get_new_name(directory, name, ".geom")

        geometry_path = os.path.join(directory, name)

        Geometry(geometry_path)

        self.project_manager.add_file(name)

        dialog.accept()

        self.update_project_list()

    def update_project_list(self):
        self.project_list_widget.clear()
        self._populate_project_tree(self.project_manager.project_files, self.project_list_widget.invisibleRootItem())

    def _populate_project_tree(self, project_files, parent_item):
        for i, item in enumerate(project_files):
            if isinstance(item, tuple):
                dir_item = QTreeWidgetItem(parent_item, [item[0]])
                dir_item.setIcon(0, QIcon('resources/icons/folder-closed.png'))
                # dir_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicator)
                self._populate_project_tree(item[1], dir_item)
            else:
                file_item = QTreeWidgetItem(parent_item, [item])
                file_item.setIcon(0, QIcon(f'resources/icons/{ICON_MAP[os.path.splitext(item)[1]]}'))
                # file_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicator)

    def new_project(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Project")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        grid_layout = QGridLayout()

        dir_label = QLabel("Directory:")
        grid_layout.addWidget(dir_label, 0, 0)

        self.dir_line_edit = QLineEdit()
        self.dir_line_edit.setText(self.root)
        grid_layout.addWidget(self.dir_line_edit, 0, 1)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_directory)
        grid_layout.addWidget(browse_button, 0, 2)

        name_label = QLabel("Project Name:")
        grid_layout.addWidget(name_label, 1, 0)

        self.name_line_edit = QLineEdit()
        self.name_line_edit.setText("New Project")
        grid_layout.addWidget(self.name_line_edit, 1, 1)

        layout.addLayout(grid_layout)

        # Dialog buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(lambda: self.create_project(dialog))
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        dialog.exec_()

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.dir_line_edit.setText(directory)

    def create_project(self, dialog):
        project_directory = self.dir_line_edit.text()
        project_name = self.name_line_edit.text()

        project_name = self.get_new_name(project_directory, project_name)

        if project_directory and project_name:
            if os.path.exists(project_directory):
                project_path = os.path.join(project_directory, project_name)
                os.makedirs(project_path, exist_ok=True)
                # Optionally add a default file to the new project directory
                # with open(os.path.join(project_path, 'default.txt'), 'w') as f:
                #     f.write('Default project file')
                self.project_manager.open_project(project_path)
                self.update_project_list()
                dialog.accept()
            else:
                QMessageBox.warning(self, "Invalid Input", "Invalid directory.")
        else:
            # You might want to show an error message to the user if the inputs are not valid
            QMessageBox.warning(self, "Invalid Input", "Both project directory and project name are required.")

    def open_project(self):
        directory = QFileDialog.getExistingDirectory(self, "Open Project Directory", self.root, QFileDialog.DontUseNativeDialog)
        if directory:
            self.project_manager.open_project(directory)
            self.update_project_list()

    def on_item_expanded(self, item):
        item.setIcon(0, QIcon("resources/icons/folder-open.png"))

    def on_item_collapsed(self, item):
        item.setIcon(0, QIcon("resources/icons/folder-closed.png"))

    def get_full_path(self, item):
        path_parts = []
        while item:
            path_parts.insert(0, item.text(0))
            item = item.parent()
        return '/'.join(path_parts)

    def on_project_list_item_selected(self):
        selected_items = self.project_list_widget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]  # Assuming single selection
            item_text = self.get_full_path(selected_item)
            self.project_manager.current_item_path = item_text
            match self.project_manager.current_tab:
                case 0:
                    if item_text.endswith(".geom"):
                        self.project_manager.open_item(item_text)
                    self.update_construct()
                    self.update_plot()

    def add_layer(self):
        self.project_manager.current_item.new_layer()
        self.update_construct()

    def add_monitor(self):
        layer_widget = LayerWidget(self.layer_list_layout, "monitor")
        layer_widget.selected.connect(lambda: self.display_layer_details(layer_widget))
        layer_widget.deselect_all.connect(self.deselect_all_layers)
        self.layer_list_layout.addWidget(layer_widget)

    def display_layer_details(self, layer):
        self.layer_details_widget.layer = layer
        self.layer_details_widget.update_properties()

        # slope, intercept = self.layer_details_widget.get_parameters()
        # self.layer_details_widget.set_parameters(slope, intercept)

    def deselect_all_layers(self):
        for i in range(self.layer_list_layout.count()):
            layer_widget = self.layer_list_layout.itemAt(i).widget()
            if layer_widget:
                layer_widget.deselect_layer()

    def update_plot(self):
        match self.project_manager.current_tab:
            case 0:
                self.project_manager.current_item.save()
                self.plot_widget.plot_geometry(self.project_manager.current_item)
