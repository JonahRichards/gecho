from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt, Signal

from gecho.geometry.geometry import Geometry


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

        validator = QDoubleValidator()
        validator.setDecimals(5)  # Set the number of allowed decimal places
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        self.zi = QLineEdit()
        self.zi.textChanged.connect(self.zi_changed)
        self.zi.setValidator(validator)

        self.zf = QLineEdit()
        self.zf.textChanged.connect(self.zf_changed)
        self.zf.setValidator(validator)

        self.emits_enabled = False

        self.update_properties()


    def zf_changed(self):
        self.layer.zf = float(self.zf.text())
        if self.emits_enabled:
            self.parameters_changed.emit()

    def zi_changed(self):
        self.layer.zi = float(self.zi.text())
        if self.emits_enabled:
            self.parameters_changed.emit()

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
            # NAME
            name_layout = QHBoxLayout()
            self.layout.addLayout(name_layout)
            name_layout.addWidget(QLabel("Layer Name: "))
            name_layout.addWidget(self.name)
            self.name.setText(self.layer.name)
            name_layout.addWidget(self.delete_button)

            self.layout.addWidget(QLabel("Z Bounds"))

            z_bounds_layout = QHBoxLayout()
            self.layout.addLayout(z_bounds_layout)

            z_bounds_layout.addWidget(QLabel("Zi: "))
            self.zi.setText(str(self.layer.zi))
            z_bounds_layout.addWidget(self.zi)
            z_bounds_layout.addWidget(QLabel("Zf: "))
            self.zf.setText(str(self.layer.zf))
            z_bounds_layout.addWidget(self.zf)

            if isinstance(self.layer, Geometry.Wall):
                self.delete_button.setDisabled(True)
            else:
                self.delete_button.setDisabled(False)

        self.emits_enabled = True

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
