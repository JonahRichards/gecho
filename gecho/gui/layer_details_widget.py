from PySide6.QtGui import QDoubleValidator, QFont, QIntValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QComboBox
from PySide6.QtCore import Qt, Signal

from gecho.geometry.geometry import Geometry


class PointsWidget(QWidget):
    parameters_changed = Signal()

    def __init__(self):
        super().__init__()

        self.boundary = None

        layout = QVBoxLayout()

        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.add_point)
        self.add_button.setFixedWidth(30)
        self.remove_button = QPushButton("-")
        self.remove_button.clicked.connect(self.remove_point)
        self.remove_button.setFixedWidth(30)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout.addLayout(button_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.points_widget = QWidget()
        self.points_layout = QVBoxLayout()
        self.points_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.points_widget.setLayout(self.points_layout)

        self.scroll_area.setWidget(self.points_widget)

        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def update_points(self):
        if self.boundary is not None:
            for i in reversed(range(self.points_layout.count())):
                self.points_layout.itemAt(i).widget().deleteLater()

            for i, point in enumerate(zip(self.boundary.zs, self.boundary.rs)):
                z, r = point
                self.points_layout.addWidget(self.create_point_widget(z, r, i))

    def create_point_widget(self, z, r, i):
        widget = QWidget()
        widget.setFixedHeight(50)
        widget.setStyleSheet("QWidget {background-color: #1b2026; border-radius: 5px; border: 1px solid #30353a;}"
                             "QLabel {background-color: #1b2026; border: none;}"
                             "QLineEdit {background-color: #0D1013; border: 1px solid #474b50; border-radius: 0px; "
                             "padding: 3px;}")

        layout = QHBoxLayout()
        widget.setLayout(layout)

        z_label = QLabel(f"z<sub>{i}</sub>")
        z_label.setFixedWidth(30)
        layout.addWidget(z_label)

        z_edit = QLineEdit(str(z))
        z_edit.textChanged.connect(self.update_zs)
        layout.addWidget(z_edit)

        r_label = QLabel(f"r<sub>{i}</sub>")
        r_label.setFixedWidth(30)
        layout.addWidget(r_label)

        r_edit = QLineEdit(str(r))
        r_edit.textChanged.connect(self.update_rs)
        layout.addWidget(r_edit)

        if i == 0 or i == len(self.boundary.zs) - 1:
            z_edit.setReadOnly(True)

        return widget

    def update_zs(self):
        try:
            self.boundary.zs = [
                float(self.points_layout.itemAt(i).widget().layout().itemAt(1).widget().text())
                for i in range(self.points_layout.count())
            ]
            self.parameters_changed.emit()
        except ValueError:
            pass

    def update_rs(self):
        try:
            self.boundary.rs = [
                float(self.points_layout.itemAt(i).widget().layout().itemAt(3).widget().text())
                for i in range(self.points_layout.count())
            ]
            self.parameters_changed.emit()
        except ValueError:
            pass

    def add_point(self):
        new_z = (self.boundary.zs[-2] + self.boundary.zs[-1]) / 2
        new_r = (self.boundary.rs[-2] + self.boundary.rs[-1]) / 2

        self.boundary.zs.insert(-1, new_z)
        self.boundary.rs.insert(-1, new_r)

        self.update_points()
        self.parameters_changed.emit()

    def remove_point(self):
        if len(self.boundary.zs) > 2:
            self.boundary.zs.pop(-2)
            self.boundary.rs.pop(-2)

            self.update_points()
            self.parameters_changed.emit()


class LayerDetailsWidget(QWidget):
    info_changed = Signal()
    parameters_changed = Signal()
    delete_layer = Signal(Geometry.Layer)

    def __init__(self):
        super().__init__()
        self.layer = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.name = QLineEdit()
        self.name.textChanged.connect(self.name_changed)

        self.delete_button = QPushButton("Delete Layer")
        self.delete_button.clicked.connect(lambda: self.delete_layer.emit(self.layer))

        float_validator = QDoubleValidator()
        float_validator.setDecimals(5)  # Set the number of allowed decimal places
        float_validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        self.zi = QLineEdit()
        self.zi.textChanged.connect(self.zi_changed)
        self.zi.setValidator(float_validator)

        self.zf = QLineEdit()
        self.zf.textChanged.connect(self.zf_changed)
        self.zf.setValidator(float_validator)

        self.ep = QLineEdit()
        self.ep.textChanged.connect(self.ep_changed)
        self.ep.setValidator(float_validator)

        self.mu = QLineEdit()
        self.mu.textChanged.connect(self.mu_changed)
        self.mu.setValidator(float_validator)

        self.sg = QLineEdit()
        self.sg.textChanged.connect(self.sg_changed)
        self.sg.setValidator(float_validator)

        self.bottom_type_select = QComboBox()
        self.bottom_type_select.addItem("Points")
        self.bottom_type_select.addItem("Function")
        self.bottom_type_select.currentIndexChanged.connect(self.bottom_type_changed)
        #self.bottom_type_select.setWindowFlags(self.bottom_type_select.windowFlags() | Qt.WindowStaysOnTopHint)

        self.bottom_points_widget = PointsWidget()
        self.bottom_points_widget.parameters_changed.connect(self.parameters_changed.emit)

        self.bottom_equation = QLineEdit()
        self.bottom_equation.textChanged.connect(self.bottom_equation_changed)

        int_validator = QIntValidator()

        self.bottom_num_points = QLineEdit()
        self.bottom_num_points.textChanged.connect(self.bottom_num_points_changed)
        self.bottom_num_points.setValidator(int_validator)

        self.top_type_select = QComboBox()
        self.top_type_select.addItem("Points")
        self.top_type_select.addItem("Function")
        self.top_type_select.currentIndexChanged.connect(self.top_type_changed)

        self.top_points_widget = PointsWidget()
        self.top_points_widget.parameters_changed.connect(self.parameters_changed.emit)

        self.top_equation = QLineEdit()
        self.top_equation.textChanged.connect(self.top_equation_changed)

        self.top_num_points = QLineEdit()
        self.top_num_points.textChanged.connect(self.top_num_points_changed)
        self.top_num_points.setValidator(int_validator)

        self.mesh_lines = QLineEdit()
        self.mesh_lines.textChanged.connect(self.mesh_lines_changed)
        self.mesh_lines.setValidator(int_validator)

        self.mesh_dx = QLineEdit()
        self.mesh_dx.textChanged.connect(self.mesh_dx_changed)
        self.mesh_dx.setValidator(float_validator)

        self.mesh_dy = QLineEdit()
        self.mesh_dy.textChanged.connect(self.mesh_dy_changed)
        self.mesh_dy.setValidator(float_validator)

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.emits_enabled = False

        self.update_properties()

    def mesh_dy_changed(self):
        try:
            self.layer.dy = float(self.mesh_dy.text())
            if self.emits_enabled:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def mesh_dx_changed(self):
        try:
            self.layer.dx = float(self.mesh_dx.text())
            if self.emits_enabled:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def mesh_lines_changed(self):
        try:
            self.layer.lines = int(self.mesh_lines.text())
            if self.emits_enabled:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def top_num_points_changed(self):
        try:
            self.layer.top.num_points = int(self.top_num_points.text())
            self.layer.top.gen_function()
            if self.emits_enabled:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def bottom_num_points_changed(self):
        try:
            self.layer.bot.num_points = int(self.bottom_num_points.text())
            self.layer.bot.gen_function()
            if self.emits_enabled:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def top_equation_changed(self):
        self.layer.top.equation_text = self.top_equation.text()
        self.layer.top.gen_function()
        if self.emits_enabled:
            self.parameters_changed.emit()

    def bottom_equation_changed(self):
        self.layer.bot.equation_text = self.bottom_equation.text()
        self.layer.bot.gen_function()
        if self.emits_enabled:
            self.parameters_changed.emit()

    def sg_changed(self):
        try:
            self.layer.sg = float(self.sg.text())
        except ValueError:
            pass

    def mu_changed(self):
        try:
            self.layer.mu = float(self.mu.text())
        except ValueError:
            pass

    def ep_changed(self):
        try:
            self.layer.ep = float(self.ep.text())
        except ValueError:
            pass

    def zf_changed(self):
        try:
            self.layer.new_zf(float(self.zf.text()))
            self.bottom_points_widget.update_points()
            if self.emits_enabled:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def zi_changed(self):
        try:
            self.layer.new_zi(float(self.zi.text()))
            self.bottom_points_widget.update_points()
            if self.emits_enabled:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def name_changed(self):
        self.layer.name = self.name.text()
        if self.emits_enabled:
            self.info_changed.emit()

    def update_properties(self):
        self.emits_enabled = False

        self.clear_layout(self.layout)

        if self.layer is None:
            pass
        else:
            u_font = QFont()
            u_font.setUnderline(True)

            # NAME
            name_layout = QHBoxLayout()
            self.layout.addLayout(name_layout)
            name_label = QLabel("Layer Name: ")
            name_layout.addWidget(name_label)
            name_layout.addWidget(self.name)
            self.name.setText(self.layer.name)
            name_layout.addWidget(self.delete_button)

            match type(self.layer):
                case Geometry.Layer | Geometry.Wall:
                    split_layout = QHBoxLayout()
                    self.layout.addLayout(split_layout)

                    left_layout = QVBoxLayout()
                    left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                    split_layout.addLayout(left_layout)

                    properties_label = QLabel("Extent")
                    properties_label.setFont(u_font)
                    left_layout.addWidget(properties_label)

                    bounds_layout = QHBoxLayout()
                    left_layout.addLayout(bounds_layout)

                    bounds_layout.addWidget(QLabel("z<sub>MIN</sub>"))
                    self.zi.setText(str(self.layer.bot.zi))
                    bounds_layout.addWidget(self.zi)
                    bounds_layout.addWidget(QLabel("z<sub>MAX</sub>"))
                    self.zf.setText(str(self.layer.bot.zf))
                    bounds_layout.addWidget(self.zf)

                    right_layout = QVBoxLayout()
                    right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                    split_layout.addLayout(right_layout)

                    materials_label = QLabel("Material Properties")
                    materials_label.setFont(u_font)
                    right_layout.addWidget(materials_label)

                    material_layout = QHBoxLayout()
                    right_layout.addLayout(material_layout)

                    material_layout.addWidget(QLabel("\u03B5"))
                    self.ep.setText(str(self.layer.ep))
                    material_layout.addWidget(self.ep)

                    material_layout.addWidget(QLabel("\u03BC"))
                    self.mu.setText(str(self.layer.mu))
                    material_layout.addWidget(self.mu)

                    material_layout.addWidget(QLabel("\u03C3"))
                    self.sg.setText(str(self.layer.sg))
                    material_layout.addWidget(self.sg)

                    bottom_label = QLabel("Boundary")
                    bottom_label.setFont(u_font)
                    left_layout.addWidget(bottom_label)

                    bottom_select_layout = QHBoxLayout()
                    left_layout.addLayout(bottom_select_layout)

                    bottom_type_label = QLabel("Type:")
                    bottom_type_label.setFixedWidth(200)
                    bottom_select_layout.addWidget(bottom_type_label)
                    bottom_select_layout.addWidget(self.bottom_type_select)

                    if isinstance(self.layer.bot, Geometry.PointBoundary):
                        self.bottom_type_select.setCurrentIndex(0)
                        self.bottom_points_widget.boundary = self.layer.bot
                        self.bottom_points_widget.update_points()
                        left_layout.addWidget(self.bottom_points_widget)
                    elif isinstance(self.layer.bot, Geometry.EquationBoundary):
                        self.bottom_type_select.setCurrentIndex(1)
                        num_points_layout = QHBoxLayout()
                        left_layout.addLayout(num_points_layout)
                        num_points_label = QLabel("Number of Points")
                        num_points_label.setFixedWidth(200)
                        num_points_layout.addWidget(num_points_label)

                        self.bottom_num_points.setText(str(self.layer.bot.num_points))
                        num_points_layout.addWidget(self.bottom_num_points)

                        left_layout.addWidget(QLabel("Boundary Equation:"))
                        self.bottom_equation.setText(self.layer.bot.equation_text)
                        left_layout.addWidget(self.bottom_equation)

                    if isinstance(self.layer, Geometry.Wall):
                        self.delete_button.setDisabled(True)
                        name_label.setText("Wall Name: ")
                    else:
                        self.delete_button.setDisabled(False)

                        bottom_label.setText("Inner Boundary")

                        top_label = QLabel("Outer Boundary")
                        top_label.setFont(u_font)
                        right_layout.addWidget(top_label)

                        top_select_layout = QHBoxLayout()
                        right_layout.addLayout(top_select_layout)

                        top_type_label = QLabel("Type:")
                        top_type_label.setFixedWidth(200)
                        top_select_layout.addWidget(top_type_label)
                        top_select_layout.addWidget(self.top_type_select)

                        if isinstance(self.layer.top, Geometry.PointBoundary):
                            self.top_type_select.setCurrentIndex(0)
                            self.top_points_widget.boundary = self.layer.top
                            self.top_points_widget.update_points()
                            right_layout.addWidget(self.top_points_widget)
                        elif isinstance(self.layer.top, Geometry.EquationBoundary):
                            self.top_type_select.setCurrentIndex(1)
                            num_points_layout = QHBoxLayout()
                            right_layout.addLayout(num_points_layout)
                            num_points_label = QLabel("Number of Points")
                            num_points_label.setFixedWidth(200)
                            num_points_layout.addWidget(num_points_label)

                            self.top_num_points.setText(str(self.layer.top.num_points))
                            num_points_layout.addWidget(self.top_num_points)

                            right_layout.addWidget(QLabel("Boundary Equation:"))
                            self.top_equation.setText(self.layer.top.equation_text)
                            right_layout.addWidget(self.top_equation)

                case Geometry.Mesh:
                    name_label.setText("Mesh Name: ")

                    properties_label = QLabel("Properties")
                    properties_label.setFont(u_font)
                    self.layout.addWidget(properties_label)

                    properties_layout = QHBoxLayout()
                    self.layout.addLayout(properties_layout)
                    properties_layout.addWidget(QLabel(""))

        self.emits_enabled = True

    def top_type_changed(self, index):
        match index:
            case 0:
                if isinstance(self.layer.top, Geometry.EquationBoundary):
                    self.layer.top = Geometry.PointBoundary()
                    self.update_properties()
                    self.parameters_changed.emit()
            case 1:
                if isinstance(self.layer.top, Geometry.PointBoundary):
                    self.layer.top = Geometry.EquationBoundary()
                    self.update_properties()
                    self.parameters_changed.emit()

    def bottom_type_changed(self, index):
        match index:
            case 0:
                if isinstance(self.layer.bot, Geometry.EquationBoundary):
                    self.layer.bot = Geometry.PointBoundary()
                    self.update_properties()
                    self.parameters_changed.emit()
                    self.bottom_type_select.setCurrentIndex(0)
            case 1:
                if isinstance(self.layer.bot, Geometry.PointBoundary):
                    self.layer.bot = Geometry.EquationBoundary()
                    self.update_properties()
                    self.parameters_changed.emit()
                    self.bottom_type_select.setCurrentIndex(1)

    def clear_layout(self, layout):
        if layout is not None:
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    if isinstance(widget, QLabel):
                        widget.deleteLater()
                    else:
                        widget.setParent(None)
                else:
                    self.clear_layout(item.layout())
