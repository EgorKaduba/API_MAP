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
        uic.loadUi('window.ui', self)

        self.map_zoom = 5
        self.map_ll = [37.977751, 55.757718]
        self.map_l = 'map'
        self.map_key = ''
        self.map_point = ''
        self.postal = False

        self.lineEdit.returnPressed.connect(self.search)
        self.pushButton.clicked.connect(self.set_layer1)
        self.pushButton_2.clicked.connect(self.set_layer2)
        self.pushButton_3.clicked.connect(self.set_layer3)
        self.pushButton_4.clicked.connect(self.sbros_metok)
        self.pushButton_5.clicked.connect(self.postal_code)

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
        if self.map_point:
            map_params['pt'] = self.map_point
        response = requests.get('https://static-maps.yandex.ru/1.x/', params=map_params)
        if not response:
            print('error: could not get map')
            return
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')

        self.g_map.setPixmap(pixmap)

    def search(self):
        x, y, adress = geo_locate(self.lineEdit.text(), self.postal)
        if x == -1 or y == -1:
            return
        self.map_ll = [x, y]
        self.map_point = f'{x},{y},comma'
        self.adres.setWordWrap(True)
        self.adres.setText(adress)
        self.refresh_map()

    def sbros_metok(self):
        self.map_point = ''
        self.adres.setText('')
        self.refresh_map()

    def postal_code(self):
        if self.pushButton_5.styleSheet() == "background-color: red;":
            self.pushButton_5.setStyleSheet("background-color: green;")
            self.postal = True
        else:
            self.pushButton_5.setStyleSheet("background-color: red;")
            self.postal = False
        self.refresh_map()


def geo_locate(name, postal):
    params = {
        'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
        'geocode': name,
        'format': 'json'
    }
    response = requests.get('http://geocode-maps.yandex.ru/1.x/', params=params)
    if not response:
        print(f'error: could not get geo_locate object {name}')
        return -1, -1
    geo_objects = response.json()['response']["GeoObjectCollection"]["featureMember"]
    if not geo_objects:
        print('error: could not get geo_objects')
        return -1, -1
    adres = [geo_objects[0]["GeoObject"]['metaDataProperty']['GeocoderMetaData']['text']]
    if 'postal_code' in geo_objects[0]["GeoObject"]['metaDataProperty']['GeocoderMetaData']['Address']:
        adres[0] = adres[0] + geo_objects[0]["GeoObject"]['metaDataProperty']['GeocoderMetaData']['Address'][
            'postal_code'] if postal else adres[0]
    return list(map(float, geo_objects[0]["GeoObject"]["Point"]["pos"].split())) + adres


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
