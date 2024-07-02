from PySide6.QtGui import QPainter, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStyleOption, QStyle
from PySide6.QtCore import Signal, Property, QSize

from gecho.geometry.geometry import Geometry


class LayerWidget(QWidget):
    selected = Signal(Geometry.Layer)
    deselect_all = Signal()

    def __init__(self, layer):
        super().__init__()

        self.layer = layer

        self.setContentsMargins(0, 0, 0, 0)

        self._selected = False
        self._highlighted = False

        self.setFixedWidth(252)

        layout = QHBoxLayout()

        if isinstance(layer, Geometry.Layer):
            self.icon = QIcon("resources/icons/layer.png")
        else:
            self.icon = QIcon("resources/icons/wall.png")

        self.icon_label = QLabel("")
        self.icon_label.setPixmap(self.icon.pixmap(QSize(30, 30)))
        self.icon_label.setFixedSize(40, 40)
        layout.addWidget(self.icon_label)

        self.label = QLabel()
        self.label.setText(layer.name)
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.mousePressEvent = self.select_layer
        self.enterEvent = self.highlight_layer
        self.leaveEvent = self.unhighlight_layer

    def delete_layer(self):
        self.parent_layout.removeWidget(self)
        self.deleteLater()

    def get_name(self):
        return self.name_input.text()

    def select_layer(self, event):
        self.deselect_all.emit()
        print("selected layer")
        self.set_selected(True)
        self.setProperty("selected", True)
        self.selected.emit(self.layer)
        self.style().unpolish(self)
        self.style().polish(self)

    def deselect_layer(self):
        self.set_selected(False)
        self.style().unpolish(self)
        self.style().polish(self)

    def highlight_layer(self, event):
        self.set_highlighted(True)
        self.style().unpolish(self)
        self.style().polish(self)

    def unhighlight_layer(self, event):
        self.set_highlighted(False)
        self.style().unpolish(self)
        self.style().polish(self)

    def is_selected(self):
        return self._selected

    def set_selected(self, value):
        self._selected = value

    def is_highlighted(self):
        return self._highlighted

    def set_highlighted(self, value):
        self._highlighted = value

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, o, p, self)

    selected_property = Property(bool, is_selected, set_selected)
    highlighted_property = Property(bool, is_highlighted, set_highlighted)


'''
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, \
    QStyleOption, QStyle
from PySide6.QtCore import Signal


class LayerWidget(QWidget):
    parameters_changed = Signal()

    def __init__(self, parent_layout):
        super().__init__()
        self.setObjectName("LayerWidget")

        self.parent_layout = parent_layout
        self.setMaximumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()

        param_layout1 = QHBoxLayout()
        param_layout1.addWidget(QLabel("Slope:"))
        self.slope_input = QLineEdit()
        self.slope_input.setPlaceholderText("Enter slope")
        param_layout1.addWidget(self.slope_input)
        layout.addLayout(param_layout1)

        param_layout2 = QHBoxLayout()
        param_layout2.addWidget(QLabel("Y-Intercept:"))
        self.intercept_input = QLineEdit()
        self.intercept_input.setPlaceholderText("Enter y-intercept")
        param_layout2.addWidget(self.intercept_input)
        layout.addLayout(param_layout2)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_layer)
        layout.addWidget(delete_button)

        # Connect the textChanged signal to a lambda function that emits the custom signal
        self.slope_input.textChanged.connect(lambda: self.parameters_changed.emit())
        self.intercept_input.textChanged.connect(lambda: self.parameters_changed.emit())

        self.setLayout(layout)

    def paintEvent(self, pe):

        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, o, p, self)

    def delete_layer(self):
        self.parent_layout.removeWidget(self)
        self.deleteLater()

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
'''