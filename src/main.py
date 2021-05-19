import sys, threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

from GUI import *


class mywindow(QMainWindow, UIMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui(self)
        self.setWindowTitle('Elevator')
        self.setWindowIcon(QIcon('../Resources/Icon/elevator.ico'))
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.setWindowOpacity(0.85)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = mywindow()
    window.show()

    sys.exit(app.exec())
