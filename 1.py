import sys

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import requests


class MainWindow(QMainWindow):
    g_map: QLabel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('main_window.ui', self)
        self.press_delta = 0.00001

        self.map_zoom = 5
        self.map_ll = [34.363991, 53.243400]
        self.map_l = 'map'
        self.map_key = ''

        self.refresh_map()

    def refresh_map(self):
        map_params = {
            "ll": ','.join(map(str, self.map_ll)),
            "l": self.map_l,
            'z': self.map_zoom
        }

        response = requests.get('https://static-maps.yandex.ru/1.x/', params=map_params)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.g_map.setPixmap(pixmap)
        self.g_map.setScaledContents(True)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
