from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal


class LayerWidget(QWidget):
    parameters_changed = Signal()

    def __init__(self, parent_layout):
        super().__init__()

        self.parent_layout = parent_layout
        self.setFixedSize(300, 100)

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
