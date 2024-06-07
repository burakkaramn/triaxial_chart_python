import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtSerialPort import QSerialPort
from data_writer import DataWriter
import threading
from firestore import FirebaseListener
import configparser
from datetime import datetime
from pyqtgraph import AxisItem
from DataLogger import DataLogger

class CustomAxisItem(AxisItem):
    def tickStrings(self, values, scale, spacing):
        strings = []
        start_time = datetime.now()
        for val in values:
            time = start_time
            string = time.strftime('%H:%M:%S')
            strings.append(string)
        return strings


class SettingsManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')

    def get_com_port(self):
        return self.config.get('AnaSayfa', 'com port')

    def get_baud_rate(self):
        return int(self.config.get('AnaSayfa', 'baud rate'))

    def get_esik_deger(self):
        return float(self.config.get('AnaSayfa', 'esik degeri'))

    def get_eksen_deger(self):
        return float(self.config.get('AnaSayfa', 'eksen degeri'))

    def get_zaman_araligi(self):
        return float(self.config.get('AnaSayfa', 'zaman araligi'))

    def get_veri_oku(self):
        return float(self.config.get('AnaSayfa', 'veri oku'))


class GercekZamanliGrafikPenceresi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.min_deger = -self.settings.get_eksen_deger()
        self.max_deger = self.settings.get_eksen_deger()
        self.veri_oku_araligi = self.settings.get_veri_oku()
        self.zaman_araligi = self.settings.get_zaman_araligi() * 600

        self.initUI()
        self.data_writer = DataWriter()
        self.data_logger = DataLogger()
        self.counter = 0  # Sayaç burada tanımlanmalı
        self.start_firebase_listener()

    def initUI(self):
        self.setWindowTitle("Gerçek Zamanlı Grafik")
        self.resize(650, 350)

        self.grafikWidget = pg.PlotWidget(axisItems={'bottom': CustomAxisItem(orientation='bottom')})
        self.grafikWidget.setLabel('left', 'İvme (m/s^2)')
        self.grafikWidget.showGrid(False, False)
        self.setCentralWidget(self.grafikWidget)

        self.veri_boyutu = int((self.zaman_araligi * 150) / 20)  # Veri boyutunu hesapla
        print("veri boyutu: ", self.veri_boyutu)

        self.veri_x = np.zeros(self.veri_boyutu, dtype=np.float64)
        self.veri_y = np.zeros(self.veri_boyutu, dtype=np.float64)
        self.veri_z = np.zeros(self.veri_boyutu, dtype=np.float64)
        self.zaman_damgaları = np.arange(self.veri_boyutu, dtype=np.float64)

        self.kurve_x = self.grafikWidget.plot(self.zaman_damgaları, self.veri_x, pen=(255, 0, 0))
        self.kurve_y = self.grafikWidget.plot(self.zaman_damgaları, self.veri_y, pen=(0, 255, 0))
        self.kurve_z = self.grafikWidget.plot(self.zaman_damgaları, self.veri_z, pen=(0, 0, 255))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.veriOku)
        self.timer.start(self.veri_oku_araligi)

        try:
            self.seri_port = QSerialPort(self.settings.get_com_port())
            self.seri_port.setBaudRate(self.settings.get_baud_rate())
            if not self.seri_port.open(QSerialPort.ReadOnly):
                raise Exception(f"Seri port açılamadı: {self.seri_port.errorString()}")
            print("Seri port bağlantısı yapıldı.")
        except Exception as e:
            print(f"Seri port bağlantısı yapılamadı: {e}")

    def veriOku(self):
        while self.seri_port.canReadLine():
            try:
                seri_veri = self.seri_port.readLine().data().decode().strip()
                #print(f"Received serial data: {seri_veri}")
                veri_xyz = [float(deger.strip()) for deger in seri_veri.split('*') if deger.strip()]

                if len(veri_xyz) == 3:
                    trueAccX, trueAccY, trueAccZ = veri_xyz

                    if abs(trueAccX) > self.settings.get_esik_deger() or abs(trueAccY) > self.settings.get_esik_deger() or abs(trueAccZ) > self.settings.get_esik_deger():
                        self.data_writer.write_data(seri_veri)
                        

                    trueAccX_cm_s2 = trueAccX
                    trueAccY_cm_s2 = trueAccY
                    trueAccZ_cm_s2 = trueAccZ
                    self.data_logger.log_data(seri_veri)

                    self.veri_x[:-1] = self.veri_x[1:]
                    self.veri_x[-1] = trueAccX_cm_s2

                    self.veri_y[:-1] = self.veri_y[1:]
                    self.veri_y[-1] = trueAccY_cm_s2

                    self.veri_z[:-1] = self.veri_z[1:]
                    self.veri_z[-1] = trueAccZ_cm_s2

                    self.zaman_damgaları[:-1] = self.zaman_damgaları[1:]
                    self.zaman_damgaları[-1] += 1

                    self.counter += 1
                    
                    if self.counter >= 5:
                        self.grafikGuncelle()
                        self.counter = 0
                else:
                    print(f"Yetersiz veri alındı: {seri_veri}")
            except Exception as e:
                print(f"Veri işleme hatası: {e}")

    def grafikGuncelle(self):
        if self.kurve_x is not None and self.kurve_y is not None and self.kurve_z is not None and self.grafikWidget is not None:
            try:
                self.kurve_x.setData(self.zaman_damgaları, self.veri_x)
                self.kurve_y.setData(self.zaman_damgaları, self.veri_y)
                self.kurve_z.setData(self.zaman_damgaları, self.veri_z)
                self.grafikWidget.setYRange(self.min_deger, self.max_deger)
            except Exception as e:
                print(f"Grafik güncelleme hatası: {e}")
        else:
            print("Grafik nesneleri silinmiş.")

    def start_firebase_listener(self):
        api_key = "your_api_key_here"
        database_url = "your_database_url_here"
        listener = FirebaseListener(api_key, database_url)
        listener_thread = threading.Thread(target=self.listen_to_firebase, args=(listener,))
        listener_thread.daemon = True
        listener_thread.start()
        print("Firebase Listener başlatıldı.")

    def listen_to_firebase(self, listener):
        for message in listener.listen_to_file():
            self.handle_firebase_message(message)

    def handle_firebase_message(self, message):
        # Firebase mesajı işleme mantığı
        print(f"Firebase'den gelen mesaj: {message}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = GercekZamanliGrafikPenceresi()
    pencere.show()
    sys.exit(app.exec_())
