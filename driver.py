import sys
from PySide6.QtWidgets import QApplication
from gecho.gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load and apply the style sheet for dark mode
    with open("gecho/gui/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
