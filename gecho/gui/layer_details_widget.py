from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Signal


class LayerDetailsWidget(QWidget):
    parameters_changed = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.slope_layout = QHBoxLayout()
        self.slope_layout.addWidget(QLabel("Slope:"))
        self.slope_input = QLineEdit()
        self.slope_input.setPlaceholderText("Enter slope")
        self.slope_layout.addWidget(self.slope_input)
        self.layout.addLayout(self.slope_layout)

        self.intercept_layout = QHBoxLayout()
        self.intercept_layout.addWidget(QLabel("Y-Intercept:"))
        self.intercept_input = QLineEdit()
        self.intercept_input.setPlaceholderText("Enter y-intercept")
        self.intercept_layout.addWidget(self.intercept_input)
        self.layout.addLayout(self.intercept_layout)

        self.setLayout(self.layout)

        self.slope_input.textChanged.connect(lambda: self.parameters_changed.emit())
        self.intercept_input.textChanged.connect(lambda: self.parameters_changed.emit())

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
