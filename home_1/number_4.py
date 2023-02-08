import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QMainWindow, QPushButton
import requests


class MainWindow(QMainWindow):
    press_delta = 5

    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)

        self.map_zoom = 5
        self.map_ll = [37.977751, 55.757718]
        self.map_l = 'map'
        self.map_key = ''

        # noinspection PyUnresolvedReferences
        self.g_layer1.clicked.connect(self.set_layer1)
        self.g_layer2.clicked.connect(self.set_layer2)
        self.g_layer3.clicked.connect(self.set_layer3)

        self.refresh_map()

    def set_layer1(self):
        self.map_l = 'map'
        self.refresh_map()

    def set_layer2(self):
        self.map_l = 'sat'
        self.refresh_map()

    def set_layer3(self):
        self.map_l = 'sat,skl'
        self.refresh_map()

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_PageUp:
            if self.map_zoom < 17:
                self.map_zoom += 1
        elif key == Qt.Key_PageDown:
            if self.map_zoom > 0:
                self.map_zoom -= 1

        elif key == Qt.Key_Escape:
            self.g_map.setFocus()

        elif key == Qt.Key_Right:
            self.map_ll[0] += self.press_delta
            if self.map_ll[0] > 180:
                self.map_ll[0] = self.map_ll[0] - 360
        elif key == Qt.Key_Left:
            self.map_ll[0] -= self.press_delta
            if self.map_ll[0] < 0:
                self.map_ll[0] = self.map_ll[0] + 360
        elif key == Qt.Key_Up:
            if self.map_ll[1] + self.press_delta < 90:
                self.map_ll[1] += self.press_delta
        elif key == Qt.Key_Down:
            if self.map_ll[1] - self.press_delta > -90:
                self.map_ll[1] -= self.press_delta
        else:
            return

        self.refresh_map()

    def refresh_map(self):
        map_params = {
            "ll": f'{self.map_ll[0]},{self.map_ll[1]}',
            "l": self.map_l,
            'z': self.map_zoom,
        }
        response = requests.get('https://static-maps.yandex.ru/1.x/', params=map_params)
        if not response:
            print('error: could not get map')
            return
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.g_map.setPixmap(pixmap)
        self.g_map.setScaledContents(True)

    def clip(v, _min, _max):
        if v < _min:
            return _min
        if v > _max:
            return _max
        return v


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
