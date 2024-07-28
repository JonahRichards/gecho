import numpy as np
from PySide6.QtGui import QDoubleValidator, QFont, QIntValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QComboBox
from PySide6.QtCore import Qt, Signal

from gecho.geometry.geometry import Geometry

types = {'wake_int_method': ["ind", "dir"],
         'modes': "list",
         'particle_motion': "int",
         'particle_field': "int",
         'current_filter': "int",
         'particle_loss': "int",
         'mesh_length': "int",
         'start_position': "float",
         'time_steps': "int",
         'step_y': "float",
         'step_z': "float",
         'n_steps_in_conductive': "int",
         'adjust_mesh': "int",
         'bunch_sigma': "float",
         'offset': "int",
         'injection_time_step': "int",
         'field_component': ["Ex", "Ey", "Ez", "Hx", "Hy", "Hz"],
         'type': ["z", "s"],
         'z_0': "float",
         'z_1': "float",
         'r_0': "float",
         'r_1': "float",
         's_0': "float",
         's_1': "float",
         'n': "int",
}


def format_string(input_string):
    input_string = input_string.replace('_0', '<sub>0</sub>')
    input_string = input_string.replace('_1', '<sub>1</sub>')
    input_string = input_string.replace('_', ' ')
    formatted_string = input_string.title()
    return formatted_string


class SimulationDetailsWidget(QWidget):
    info_changed = Signal()
    parameters_changed = Signal()
    delete_layer = Signal(Geometry.Layer)

    def __init__(self):
        super().__init__()
        self.geom = Geometry()
        self.geom.new_monitor()
        self.comp = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.name = QLineEdit()
        self.name.textChanged.connect(self.name_changed)

        self.delete_button = QPushButton("Delete Monitor")
        self.delete_button.clicked.connect(lambda: self.delete_layer.emit(self.comp))

        float_validator = QDoubleValidator()
        float_validator.setDecimals(5)  # Set the number of allowed decimal places
        float_validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        int_validator = QIntValidator()

        components = ["model", "mesh", "beam", "monitors"]

        for comp_name in components:
            comp = getattr(self.geom, comp_name)
            comp = comp[0] if isinstance(comp, list) else comp
            atts = [v for v in comp.__dict__.keys() if v in types.keys()]

            for att in atts:
                match types[att]:
                    case "int":
                        setattr(self, f"{comp_name}_{att}", QLineEdit())
                        line_edit = getattr(self, f"{comp_name}_{att}")
                        line_edit.textChanged.connect(lambda _, cn=comp_name, a=att: self.numeric_changed(cn, a, int))
                        line_edit.setValidator(int_validator)
                    case "float":
                        setattr(self, f"{comp_name}_{att}", QLineEdit())
                        line_edit = getattr(self, f"{comp_name}_{att}")
                        line_edit.textChanged.connect(lambda _, cn=comp_name, a=att: self.numeric_changed(cn, a, float, update=True))
                        line_edit.setValidator(float_validator)
                    case "list":
                        setattr(self, f"{comp_name}_{att}", QLineEdit())
                        line_edit = getattr(self, f"{comp_name}_{att}")
                        line_edit.textChanged.connect(lambda _, cn=comp_name, a=att: self.list_changed(cn, a))
                    case items:
                        setattr(self, f"{comp_name}_{att}", QComboBox())
                        combo_box = getattr(self, f"{comp_name}_{att}")
                        for item in items:
                            combo_box.addItem(item)
                        combo_box.currentIndexChanged.connect(lambda i, cn=comp_name, a=att: self.combo_changed(i, cn, a))

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.emits_enabled = False

        self.update_parameters()

    def combo_changed(self, index, component, attribute, update=False):
        combo_box = getattr(self, f"{component}_{attribute}")
        setattr(self.comp, attribute, combo_box.itemText(index))
        self.geom.save()
        if update:
            self.parameters_changed.emit()

    def list_changed(self, component, attribute, update=False):
        try:
            line_edit = getattr(self, f"{component}_{attribute}")
            text = line_edit.text().replace(",", " ")
            setattr(self.comp, attribute, [int(v) for v in text.split()])
            self.geom.save()
            if update:
                self.parameters_changed.emit()
        except ValueError:
            pass

    def numeric_changed(self, component, attribute, dtype, update=False):
        try:
            line_edit = getattr(self, f"{component}_{attribute}")
            setattr(self.comp, attribute, dtype(line_edit.text()))
            self.geom.save()
            if update:
                self.parameters_changed.emit()
        except ValueError as e:
            pass

    def name_changed(self):
        self.comp.name = self.name.text()
        if self.emits_enabled:
            self.info_changed.emit()

    def update_parameters(self):
        self.emits_enabled = False

        self.clear_layout(self.layout)

        if self.comp is None:
            pass
        else:
            match type(self.comp):
                case Geometry.Model:
                    self.display_comp("model")
                case Geometry.Mesh:
                    self.display_comp("mesh")
                case Geometry.Beam:
                    self.display_comp("beam")
                case Geometry.Monitor:
                    self.display_comp("monitors")

        self.emits_enabled = True

    def display_comp(self, comp_name):
        u_font = QFont()
        u_font.setUnderline(True)

        if isinstance(self.comp, Geometry.Monitor):
            name_layout = QHBoxLayout()
            self.layout.addLayout(name_layout)
            name_label = QLabel("Monitor Name: ")
            name_layout.addWidget(name_label)
            name_layout.addWidget(self.name)
            self.name.setText(self.comp.name)
            name_layout.addWidget(self.delete_button)
        else:
            label = QLabel(f"{comp_name.title()}")
            label.setFont(u_font)
            self.layout.addWidget(label)

        atts = [v for v in self.comp.__dict__.keys() if v in types.keys()]

        for att in atts:
            layout = QHBoxLayout()
            self.layout.addLayout(layout)
            label = QLabel(f"{format_string(att)}:")
            label.setFixedWidth(200)
            layout.addWidget(label)
            widget = getattr(self, f"{comp_name}_{att}")
            if isinstance(widget, QLineEdit):
                widget.setText(str(getattr(self.comp, att)).strip("[]"))
            else:
                assert isinstance(widget, QComboBox)
                widget.setCurrentIndex(types[att].index(str(getattr(self.comp, att))))
            layout.addWidget(widget)

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
