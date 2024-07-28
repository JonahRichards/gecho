import sys
import os
from PySide6.QtWidgets import QApplication
from gecho.gui.main_window import MainWindow

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        application_path = "".join([i + '\\' for i in sys.executable.split('\\')[0:-1]])
    else:
        application_path = os.path.dirname(os.path.abspath(__file__)) + '\\'

    app = QApplication(sys.argv)
    with open("resources/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = MainWindow(application_path)
    window.show()
    sys.exit(app.exec())
