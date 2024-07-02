from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt, Signal

from gecho.geometry.geometry import Geometry


class LayerDetailsWidget(QWidget):
    parameters_changed = Signal()

    def __init__(self):
        super().__init__()
        self.layer = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.name = QLineEdit()

        self.delete_button = QPushButton("Delete Layer")

        self.update()

        # self.slope_layout = QHBoxLayout()
        # self.slope_layout.addWidget(QLabel("Slope:"))
        # self.slope_input = QLineEdit()
        # self.slope_input.setPlaceholderText("Enter slope")
        # self.slope_layout.addWidget(self.slope_input)
        # self.layout.addLayout(self.slope_layout)
        #
        # self.intercept_layout = QHBoxLayout()
        # self.intercept_layout.addWidget(QLabel("Y-Intercept:"))
        # self.intercept_input = QLineEdit()
        # self.intercept_input.setPlaceholderText("Enter y-intercept")
        # self.intercept_layout.addWidget(self.intercept_input)
        # self.layout.addLayout(self.intercept_layout)
        #
        # self.slope_input.textChanged.connect(lambda: self.parameters_changed.emit())
        # self.intercept_input.textChanged.connect(lambda: self.parameters_changed.emit())

    def update_properties(self):
        self.clear_layout(self.layout)

        if self.layer is None:
            pass
        else:
            name_layout = QHBoxLayout()
            self.layout.addLayout(name_layout)

            name_layout.addWidget(self.name)
            self.name.setText(self.layer.name)

            name_layout.addWidget(self.delete_button)

            if isinstance(self.layer, Geometry.Wall):
                self.delete_button.setDisabled(True)
            else:
                self.delete_button.setDisabled(False)

    def clear_layout(self, layout):
        if layout is not None:
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.clear_layout(item.layout())

    def boxdelete(self, box):
        for i in range(self.vlayout.count()):
            layout_item = self.vlayout.itemAt(i)
            if layout_item.layout() == box:
                self.clear_layout(layout_item.layout())
                self.vlayout.removeItem(layout_item)
                break

    def set_parameters(self, slope, intercept):
        self.slope_input.setText(str(slope))
        self.intercept_input.setText(str(intercept))

    def get_parameters(self):
        try:
            slope = float(self.slope_input.text())
        except ValueError:
            slope = 0.0
        try:
            intercept = float(self.intercept_input.text())
        except ValueError:
            intercept = 0.0
        return slope, intercept
