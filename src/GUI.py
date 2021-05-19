from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QMessageBox
from Dispatcher import Dispatcher
import image

CLOSE = 0
OPEN = 1
STOP = 0
UP = 1
DOWN = 2
PAUSE = 0
PLAY = 1


class Elevators:
    def __init__(self):
        self.elevator_background = []
        self.elevator_front_left = []
        self.elevator_front_right = []
        self.elevator_animation_left = []
        self.elevator_animation_right = []
        self.floor_lcd = []
        self.status_light = []
        self.up_button = []
        self.down_button = []
        self.warning_button = []
        self.floor_button_positions = []
        self.floor_buttons = []
        self.elevator_working = [True] * 5
        self.elevator_state = [STOP] * 5
        self.animation = [PAUSE] * 5
        self.elevator_floor = [1] * 5
        self.stop_queue = [[], [], [], [], []]
        self.wait_queue = [[], [], [], [], []]
        self.inside_buttons = []
        self.up_wait_list = []
        self.down_wait_list = []


class UIMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("init:.")

        self.elevators = Elevators()
        self.dispatcher = Dispatcher(self.elevators)

    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("UIMainWindow")
        MainWindow.resize(1366, 768)
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")

        elevator_position = [30, 280, 530, 780, 1030]

        for i in range(len(elevator_position)):
            elevator_background = QtWidgets.QGraphicsView(self)
            elevator_background.setGeometry(QtCore.QRect(elevator_position[i], 550, 131, 161))
            elevator_background.setStyleSheet("background-color: rgb(0, 0, 0);")
            elevator_background.setObjectName("elevator_background" + str(i))
            self.elevators.elevator_background.append(elevator_background)

            elevator_front_left = QtWidgets.QGraphicsView(self)
            elevator_front_left.setGeometry(QtCore.QRect(elevator_position[i], 550, 64, 161))
            elevator_front_left.setStyleSheet("background-color: rgb(160, 160, 160);")
            elevator_front_left.setObjectName("elevator_front_left" + str(i))
            self.elevators.elevator_front_left.append(elevator_front_left)
            elevator_animation_left_open = QPropertyAnimation(self.elevators.elevator_front_left[i], b"geometry")
            elevator_animation_left_open.setDuration(1000)
            elevator_animation_left_open.setStartValue(QtCore.QRect(elevator_position[i], 550, 64, 161))
            elevator_animation_left_open.setEndValue(QtCore.QRect(elevator_position[i], 550, 8, 161))
            elevator_animation_left_close = QPropertyAnimation(self.elevators.elevator_front_left[i], b"geometry")
            elevator_animation_left_close.setDuration(1000)
            elevator_animation_left_close.setStartValue(QtCore.QRect(elevator_position[i], 550, 8, 161))
            elevator_animation_left_close.setEndValue(QtCore.QRect(elevator_position[i], 550, 64, 161))
            elevator_animation_left = QSequentialAnimationGroup()
            elevator_animation_left.addAnimation(elevator_animation_left_open)
            elevator_animation_left.addPause(1000)
            elevator_animation_left.addAnimation(elevator_animation_left_close)
            self.elevators.elevator_animation_left.append(elevator_animation_left)

            elevator_front_right = QtWidgets.QGraphicsView(self)
            elevator_front_right.setGeometry(QtCore.QRect(elevator_position[i] + 67, 550, 64, 161))
            elevator_front_right.setStyleSheet("background-color: rgb(160, 160, 160);")
            elevator_front_right.setObjectName("elevator_front_right" + str(i))
            self.elevators.elevator_front_right.append(elevator_front_right)
            elevator_animation_right_open = QPropertyAnimation(self.elevators.elevator_front_right[i], b"geometry")
            elevator_animation_right_open.setDuration(1000)
            elevator_animation_right_open.setStartValue(QtCore.QRect(elevator_position[i] + 67, 550, 64, 161))
            elevator_animation_right_open.setEndValue(QtCore.QRect(elevator_position[i] + 123, 550, 8, 161))
            elevator_animation_right_close = QPropertyAnimation(self.elevators.elevator_front_right[i], b"geometry")
            elevator_animation_right_close.setDuration(1000)
            elevator_animation_right_close.setStartValue(QtCore.QRect(elevator_position[i] + 123, 550, 8, 161))
            elevator_animation_right_close.setEndValue(QtCore.QRect(elevator_position[i] + 67, 550, 64, 161))
            elevator_animation_right = QSequentialAnimationGroup()
            elevator_animation_right.addAnimation(elevator_animation_right_open)
            elevator_animation_right.addPause(1000)
            elevator_animation_right.addAnimation(elevator_animation_right_close)
            self.elevators.elevator_animation_right.append(elevator_animation_right)

        font = QtGui.QFont()
        font.setFamily("AcadEref")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)

        label_position = [70, 320, 570, 820, 1070]
        for i in range(0, len(label_position)):
            label = QtWidgets.QLabel(self)
            label.setGeometry(QtCore.QRect(label_position[i], 720, 51, 21))
            label.setFont(font)
            self.setStyleSheet("background-color: rgb(160, 160, 160);")
            label.setObjectName("label" + str(i))
            label.setText("电梯" + str(i + 1))

        floor_lcd_position = [50, 300, 550, 800, 1050]
        for i in range(0, len(floor_lcd_position)):
            floor = QtWidgets.QLCDNumber(self)
            floor.setGeometry(floor_lcd_position[i], 490, 51, 41)
            floor.setDigitCount(2)
            floor.setProperty("value", 1.0)  # 设置初始楼层为1层
            floor.setObjectName("floor" + str(i))
            floor.setStyleSheet("color: red;")
            self.elevators.floor_lcd.append(floor)

        status_position = [95, 345, 595, 845, 1095]
        for i in range(0, len(status_position)):
            status = QtWidgets.QGraphicsView(self)
            status.setGeometry(QtCore.QRect(status_position[i], 480, 71, 61))
            status.setStyleSheet("QGraphicsView{border-image: url(:/Resources/Button/state.png)}")
            status.setObjectName("status" + str(i))
            self.elevators.status_light.append(status)

        warning_position = [180, 430, 680, 930, 1180]
        for i in range(0, len(warning_position)):
            warning_button = QtWidgets.QPushButton(self)
            warning_button.setGeometry(QtCore.QRect(warning_position[i] + 10, 660, 56, 31))
            warning_button.setStyleSheet("background-color: rgb(180, 0, 0);color: white;")
            warning_button.setObjectName("warning_button" + str(i))
            warning_button.clicked.connect(MainWindow.warning_button_clicked)
            warning_button.setText("警报")
            self.elevators.warning_button.append(warning_button)

        # 使用栅格布局添加内部按钮
        floor_button_positions = [170, 420, 670, 920, 1170]

        for i in range(0, len(floor_button_positions)):
            floor_button_position = QtWidgets.QWidget(self)
            floor_button_position.setGeometry(QtCore.QRect(floor_button_positions[i] + 10, 200, 81, 451))
            floor_button_position.setObjectName("floor_button_positions" + str(i))
            self.elevators.floor_button_positions.append(floor_button_position)

            floor_buttons = QtWidgets.QGridLayout(self.elevators.floor_button_positions[i])
            floor_buttons.setContentsMargins(0, 0, 0, 0)
            floor_buttons.setObjectName("floor_buttons" + str(i))
            self.elevators.floor_buttons.append(floor_buttons)

        names = ['19', '20', '17', '18', '15', '16', '13', '14', '11', '12', '9', '10', '7', '8', '5', '6', '3',
                 '4', '1', '2']

        positions = [(i, j) for i in range(10) for j in range(2)]
        for i in range(0, len(floor_button_positions)):
            for position, name in zip(positions, names):
                button = QtWidgets.QPushButton(name)
                button.setObjectName("button " + str(i) + ' ' + name)
                button.setStyleSheet("")
                button.clicked.connect(MainWindow.inside_button_click)
                self.elevators.floor_buttons[i].addWidget(button, *position)
                self.elevators.inside_buttons.append(button)

        # 添加每一层的按钮
        floor_button_layout = QtWidgets.QWidget(self)
        floor_button_layout.setGeometry(QtCore.QRect(50, 20, 1200, 180))
        floor_button_layout.setObjectName("floor_button_layout")
        grid = QtWidgets.QGridLayout(floor_button_layout)
        grid.setVerticalSpacing(0)
        grid.setRowMinimumHeight(1, 40)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setObjectName("floor_button_grid")

        names = ['1', 'up', 'down', '2', 'up', 'down', '3', 'up', 'down', '4', 'up', 'down', '5', 'up', 'down',
                 '6', 'up', 'down', '7', 'up', 'down', '8', 'up', 'down', '9', 'up', 'down', '10', 'up', 'down',
                 '11', 'up', 'down', '12', 'up', 'down', '13', 'up', 'down', '14', 'up', 'down', '15', 'up', 'down',
                 '16', 'up', 'down', '17', 'up', 'down', '18', 'up', 'down', '19', 'up', 'down', '20', 'up', 'down']
        positions = [(i, j) for i in range(2) for j in range(30)]
        count = 0
        for position, name in zip(positions, names):
            if name == 'up':
                up_button = QtWidgets.QPushButton(self)
                up_button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/up.png)}"
                                        "QPushButton:hover{border-image: url(:/Resources/Button/up_hover.png)}"
                                        "QPushButton:pressed{border-image: url(:/Resources/Button/up_pressed.png)}")
                up_button.setMinimumSize(32, 32)
                up_button.setObjectName("up_button " + str(count // 3 + 1))
                up_button.clicked.connect(MainWindow.outside_button_click)
                self.elevators.up_button.append(up_button)
                grid.addWidget(up_button, *position)
            elif name == 'down':
                down_button = QtWidgets.QPushButton(self)
                down_button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/down.png)}"
                                          "QPushButton:hover{border-image: url(:/Resources/Button/down_hover.png)}"
                                          "QPushButton:pressed{border-image: url(:/Resources/Button/down_pressed.png)}")
                down_button.setObjectName("down_button " + str(count // 3 + 1))
                down_button.clicked.connect(MainWindow.outside_button_click)
                down_button.setMinimumSize(32, 32)
                self.elevators.down_button.append(down_button)
                grid.addWidget(down_button, *position)
            else:
                floor = QtWidgets.QLabel(name)
                floor.setObjectName("floor" + str(name))
                floor.setStyleSheet("font-size:28px;")
                floor.setAlignment(Qt.AlignRight)
                grid.addWidget(floor, *position)

            count += 1

    def warning_button_clicked(self):
        warning_button = int(self.sender().objectName()[-1])
        print(f"乘客按下了警报器{warning_button}")
        self.elevators.warning_button[warning_button].setStyleSheet("background-color: rgb(255, 255, 255);")
        self.elevators.warning_button[warning_button].setStyleSheet("background-color: rgb(180, 0, 0);")
        elevator_work = self.dispatcher.warning_control(warning_button)
        if not elevator_work:
            QMessageBox.warning(self, "警告", "所有电梯均停止工作！")

    def inside_button_click(self):
        floor_button = self.sender()
        button_information = [int(s) for s in floor_button.objectName().split(' ') if s.isdigit()]
        elevator = button_information[0]
        floor = button_information[1]
        floor_button.setStyleSheet("background-color: rgb(255,150,3);")
        floor_button.setEnabled(False)

        self.dispatcher.elevator_move(elevator, floor)

    def outside_button_click(self):
        floor = int(self.sender().objectName().split()[1])
        direction = STOP
        direction_string = ""
        if self.sender().objectName().split()[0][0] == 'u':
            direction = UP
            direction_string = "上"
            button = self.elevators.up_button[floor - 1]
            button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/up_pressed.png)}")
            button.setEnabled(False)
        else:
            direction = DOWN
            direction_string = "下"
            button = self.elevators.down_button[floor - 1]
            button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/down_pressed.png)}")
            button.setEnabled(False)
        print(f"乘客在{floor}层，想要往{direction_string}")
        self.dispatcher.dispatch(floor, direction)
