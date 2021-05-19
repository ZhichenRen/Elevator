from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
import image

CLOSE = 0
OPEN = 1
STOP = 0
UP = 1
DOWN = 2
AT_DESTINATION = 3
PAUSE = 0
ANIMATION_OPEN = 3
ANIMATION_WAIT = 2
ANIMATION_CLOSE = 1


class Dispatcher:
    def __init__(self, elevators):
        self.elevators = elevators

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elevator_status)
        self.timer.start(1000)

    def warning_control(self, elevator):
        self.elevators.elevator_working[elevator] = False
        self.elevators.warning_button[elevator].setEnabled(False)
        self.elevators.floor_button_positions[elevator].setEnabled(False)
        self.elevators.elevator_front_left[elevator].setEnabled(False)
        self.elevators.elevator_front_right[elevator].setEnabled(False)
        self.elevators.floor_lcd[elevator].setEnabled(False)
        self.elevators.elevator_state[elevator] = STOP
        self.elevators.stop_queue[elevator].clear()
        self.elevators.wait_queue[elevator].clear()
        while len(self.elevators.out_command_list[elevator]) != 0:
            floor = self.elevators.out_command_list[elevator].pop(0)
            self.elevators.up_wait_list.append(floor)

        for inside_button in self.elevators.inside_buttons:
            if f"button {elevator}" in inside_button.objectName():
                inside_button.setStyleSheet("")

        check = False
        for i in range(5):
            if self.elevators.elevator_working[i]:
                check = True
        if not check:
            return False
        return True

    def open_door_animation(self, elevator):
        print(f"电梯{elevator + 1}开门中")
        self.elevators.animation[elevator] = ANIMATION_OPEN
        self.elevators.elevator_animation_left[elevator].start()
        self.elevators.elevator_animation_right[elevator].start()

    def elevator_move(self, elevator, to_floor):
        from_floor = self.elevators.elevator_floor[elevator]
        print(f"乘客在{elevator + 1}号电梯{from_floor}层，想去{to_floor}层")
        if from_floor < to_floor:
            if self.elevators.elevator_state[elevator] == STOP:
                self.elevators.stop_queue[elevator].append(to_floor)
            else:
                if self.elevators.elevator_state[elevator] == UP:
                    self.elevators.stop_queue[elevator].append(to_floor)
                    self.elevators.stop_queue[elevator].sort()
                else:
                    self.elevators.wait_queue[elevator].append(to_floor)
        elif from_floor > to_floor:
            if self.elevators.elevator_state[elevator] == STOP:
                self.elevators.stop_queue[elevator].append(to_floor)
            else:
                if self.elevators.elevator_state[elevator] == DOWN:
                    self.elevators.stop_queue[elevator].append(to_floor)
                    self.elevators.stop_queue[elevator].sort(reverse=True)
                else:
                    self.elevators.wait_queue[elevator].append(to_floor)

    def dispatch(self, to_floor, direction):
        distance = [100] * 5
        best_choice = -1
        min_distance = 100
        for i in range(5):
            if not self.elevators.elevator_working[i]:
                continue
            if direction == self.elevators.elevator_state[i]:
                if direction == UP and to_floor > self.elevators.elevator_floor[i]:
                    distance[i] = abs(to_floor - self.elevators.elevator_floor[i]) + 2 * len(
                        self.elevators.stop_queue[i])
                elif direction == DOWN and to_floor < self.elevators.elevator_floor[i]:
                    distance[i] = abs(to_floor - self.elevators.elevator_floor[i]) + 2 * len(
                        self.elevators.stop_queue[i])
            elif self.elevators.elevator_state[i] == STOP:
                distance[i] = abs(to_floor - self.elevators.elevator_floor[i]) + 2 * len(self.elevators.stop_queue[i])

            if distance[i] < min_distance:
                best_choice = i
                min_distance = distance[i]

        if best_choice >= 0:
            if distance[best_choice] == 0:
                self.open_door_animation(best_choice)
                up_button = self.elevators.up_button[to_floor - 1]
                up_button.setEnabled(True)
                up_button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/up.png)}"
                                        "QPushButton:hover{border-image: url(:/Resources/Button/up_hover.png)}"
                                        "QPushButton:pressed{border-image: url(:/Resources/Button/up_pressed.png)}")
                down_button = self.elevators.down_button[to_floor - 1]
                down_button.setEnabled(True)
                down_button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/down.png)}"
                                          "QPushButton:hover{border-image: url(:/Resources/Button/down_hover.png)}"
                                          "QPushButton:pressed{border-image: url(:/Resources/Button/down_pressed.png)}")

            else:
                self.elevators.out_command_list[best_choice].append(to_floor)
                self.elevators.stop_queue[best_choice].append(to_floor)
                if self.elevators.elevator_state[best_choice] == UP:
                    self.elevators.stop_queue[best_choice].sort()
                else:
                    self.elevators.stop_queue[best_choice].sort(reverse=True)
        else:
            if direction == UP:
                self.elevators.up_wait_list.append(to_floor)
            else:
                self.elevators.down_wait_list.append(to_floor)

    def update_elevator_status(self):
        # 重新分配外部等待队列中的任务
        length = len(self.elevators.up_wait_list)
        for _ in range(length):
            to_floor = self.elevators.up_wait_list[0]
            self.elevators.up_wait_list.pop(0)
            self.dispatch(to_floor, UP)
        length = len(self.elevators.down_wait_list)
        for _ in range(length):
            to_floor = self.elevators.down_wait_list[0]
            self.elevators.down_wait_list.pop(0)
            self.dispatch(to_floor, DOWN)
        for i in range(5):
            if len(self.elevators.stop_queue[i]):
                to_floor = self.elevators.stop_queue[i][0]

                if self.elevators.elevator_state[i] == AT_DESTINATION:
                    self.open_door_animation(i)
                    button = self.elevators.inside_buttons[0]
                    for inside_button in self.elevators.inside_buttons:
                        if inside_button.objectName() == f"button {i} {to_floor}":
                            button = inside_button
                    button.setStyleSheet("")
                    button.setEnabled(True)
                    up_button = self.elevators.up_button[to_floor - 1]
                    up_button.setEnabled(True)
                    up_button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/up.png)}"
                                            "QPushButton:hover{border-image: url(:/Resources/Button/up_hover.png)}"
                                            "QPushButton:pressed{border-image: url(:/Resources/Button/up_pressed.png)}")
                    down_button = self.elevators.down_button[to_floor - 1]
                    down_button.setEnabled(True)
                    down_button.setStyleSheet("QPushButton{border-image: url(:/Resources/Button/down.png)}"
                                              "QPushButton:hover{border-image: url(:/Resources/Button/down_hover.png)}"
                                              "QPushButton:pressed{border-image: url(:/Resources/Button/down_pressed.png)}")
                    stop_floor = self.elevators.stop_queue[i].pop(0)
                    if stop_floor in self.elevators.out_command_list[i]:
                        self.elevators.out_command_list[i].remove(stop_floor)
                    if len(self.elevators.stop_queue[i]) == 0:
                        if len(self.elevators.wait_queue[i]) == 0:
                            self.elevators.elevator_state[i] = STOP
                            self.elevators.status_light[i].setStyleSheet(
                                "QGraphicsView{border-image: url(:/Resources/Button/state.png)}")
                        else:
                            self.elevators.stop_queue[i] = self.elevators.wait_queue[i][:]
                            self.elevators.wait_queue[i].clear()
                            if self.elevators.elevator_state == UP:
                                self.elevators.stop_queue[i].sort(reverse=True)
                            elif self.elevators.elevator_state == DOWN:
                                self.elevators.stop_queue[i].sort()
                    if len(self.elevators.stop_queue[i]) != 0:
                        if self.elevators.elevator_floor[i] < self.elevators.stop_queue[i][0]:
                            self.elevators.elevator_state[i] = UP
                        else:
                            self.elevators.elevator_state[i] = DOWN
                elif self.elevators.animation[i] != PAUSE:
                    self.elevators.animation[i] -= 1
                else:
                    if to_floor > self.elevators.elevator_floor[i]:
                        self.elevators.elevator_state[i] = UP
                        self.elevators.status_light[i].setStyleSheet(
                            "QGraphicsView{border-image: url(:/Resources/Button/state_up.png)}")
                        self.elevators.elevator_floor[i] += 1
                        self.elevators.floor_lcd[i].setProperty("value", self.elevators.elevator_floor[i])
                    elif to_floor < self.elevators.elevator_floor[i]:
                        self.elevators.elevator_state[i] = DOWN
                        self.elevators.status_light[i].setStyleSheet(
                            "QGraphicsView{border-image: url(:/Resources/Button/state_down.png)}")
                        self.elevators.elevator_floor[i] -= 1
                        self.elevators.floor_lcd[i].setProperty("value", self.elevators.elevator_floor[i])
                    else:
                        self.elevators.elevator_state[i] = AT_DESTINATION
            else:
                self.elevators.elevator_state[i] = STOP
                self.elevators.status_light[i].setStyleSheet(
                    "QGraphicsView{border-image: url(:/Resources/Button/state.png)}")
