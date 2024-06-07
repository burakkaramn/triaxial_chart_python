import os
import time
import threading
import requests
from datetime import datetime

class FirebaseListener:
    def __init__(self, api_key, database_url):
        # Firebase bağlantı detayları
        self.api_key = api_key
        self.database_url = database_url

        # Data.txt dosyası
        self.filename = 'data.txt'
        self.last_line = None

        # Log dosyalarının saklanacağı klasör
        self.log_directory = 'log'
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        # Uygulama başladığında Firestore'u sıfırla ve son satırı kaydet
        self.reset_firestore_initial()
        self.set_initial_last_line()

    def reset_firestore_initial(self):
        try:
            url = f"{self.database_url}?key={self.api_key}"
            data = {'fields': {'deger': {'integerValue': 0}}}
            response = requests.patch(url, json=data)
            if response.status_code == 200:
                print("Firestore başlangıçta güncellendi: deger = 0")
            else:
                print(f"Firestore güncelleme hatası: {response.text}")
        except Exception as e:
            print(f"Firestore güncelleme hatası: {e}")

    def set_initial_last_line(self):
        try:
            with open(self.filename, 'r') as file:
                lines = file.readlines()
                if lines:
                    self.last_line = lines[-1].strip()
                    print(f"Başlangıçta son satır kaydedildi: {self.last_line}")
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")

    def listen_to_file(self):
        while True:
            with open(self.filename, 'r') as file:
                lines = file.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line != self.last_line:
                        self.last_line = last_line
                        print(f"Yeni veri tespit edildi: {last_line}")
                        self.update_firestore()

            time.sleep(1)  # Dosyayı 1 saniye aralıklarla kontrol et

    def update_firestore(self):
        try:
            url = f"{self.database_url}?key={self.api_key}"
            data = {'fields': {'deger': {'integerValue': 1}}}
            response = requests.patch(url, json=data)
            if response.status_code == 200:
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.log_to_file(f"{timestamp} - Firestore güncellendi: deger = 1")
                print("Firestore güncellendi: deger = 1")

                # 30 saniye sonra değeri tekrar 0 yap
                threading.Timer(2.0, self.reset_firestore).start()
            else:
                print(f"Firestore güncelleme hatası: {response.text}")
        except Exception as e:
            print(f"Firestore güncelleme hatası: {e}")

    def reset_firestore(self):
        try:
            url = f"{self.database_url}?key={self.api_key}"
            data = {'fields': {'deger': {'integerValue': 0}}}
            response = requests.patch(url, json=data)
            if response.status_code == 200:
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.log_to_file(f"{timestamp} - Firestore güncellendi: deger = 0")
                print("Firestore güncellendi: deger = 0")
            else:
                print(f"Firestore güncelleme hatası: {response.text}")
        except Exception as e:
            print(f"Firestore güncelleme hatası: {e}")

    def log_to_file(self, message):
        date_str = datetime.now().strftime('%d_%m_%Y')
        filename = os.path.join(self.log_directory, f"{date_str}.txt")
        with open(filename, 'a') as file:
            file.write(message + '\n')

def start_firebase_listener():
    api_key = "AIzaSyDh0Pj3Y9Qvpj_ZaxXNo0_NdZ-jaqsV12k"
    database_url = "https://firestore.googleapis.com/v1/projects/earlywarning-ef60f/databases/(default)/documents/data/message"
    listener = FirebaseListener(api_key, database_url)
    listener_thread = threading.Thread(target=listener.listen_to_file)
    listener_thread.daemon = True
    listener_thread.start()
    print("Firebase Listener başlatıldı.")
