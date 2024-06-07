import tkinter as tk
from tkinter import ttk
import subprocess
import configparser


class Arayuz(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sismik Çizim")

        # Ayarları yükle
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')

        # Ayarları yükleyerek değişkenleri ayarla
        self.com_port_default = self.config.get('AnaSayfa', 'com port')
        self.baud_rate_default = self.config.get('AnaSayfa', 'baud rate')
        self.esik_deger_default = self.config.get('AnaSayfa', 'esik degeri')
        self.eksen_deger_default = self.config.get('AnaSayfa', 'eksen degeri')
        self.zaman_araligi_defaut = self.config.get('AnaSayfa', 'zaman araligi') 
        self.veri_oku_defaut = self.config.get('AnaSayfa', 'veri oku')

        # Initialize NoteBook (similar to QStackedWidget)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # ANA SAYFA OLUŞTURMA
        self.home_page = tk.Frame(self.notebook)
        self.initialize_home_page(self.home_page)
        self.notebook.add(self.home_page, text="Genel")

        # Ayarları yükle
        self.load_settings()

        # Start the serial reader process
        self.start_serial_reader()

    def load_settings(self):
        # Ayarları kullanarak giriş alanlarını doldur
        self.com_port_entry.insert(0, self.com_port_default)
        self.baud_rate_combobox.set(self.baud_rate_default)
        self.esik_deger_entry.insert(0, self.esik_deger_default)
        self.eksen_deger_entry.insert(0, self.eksen_deger_default)
        self.zaman_araligi_entry.insert(0,self.zaman_araligi_defaut)
        self.veri_oku_entry.insert(0,self.veri_oku_defaut)

    def initialize_home_page(self, home_page):
        calisma_modu = tk.LabelFrame(home_page, text="Çalışma Modu")
        calisma_modu.pack()

        # COM PORT
        com_port_label = tk.Label(calisma_modu, text="COM Port:")
        com_port_label.grid(row=0, column=0)
        self.com_port_entry = tk.Entry(calisma_modu)
        self.com_port_entry.grid(row=0, column=1)

        # BAUD RATE
        baud_rate_label = tk.Label(calisma_modu, text="Baud Rate:")
        baud_rate_label.grid(row=1, column=0)
        self.baud_rate_combobox = ttk.Combobox(calisma_modu, values=["110", "300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "38400", "57600", "115200", "128000", "256000"])
        self.baud_rate_combobox.grid(row=1, column=1)

        # EŞİK DEĞER
        esik_deger_label = tk.Label(calisma_modu, text="Eşik Değeri:")
        esik_deger_label.grid(row=2, column=0)
        self.esik_deger_entry = tk.Entry(calisma_modu)
        self.esik_deger_entry.grid(row=2, column=1)

        # EKSEN DEĞER
        eksen_deger_label = tk.Label(calisma_modu, text="Y Eksen Değeri:")
        eksen_deger_label.grid(row=3, column=0)
        self.eksen_deger_entry = tk.Entry(calisma_modu)
        self.eksen_deger_entry.grid(row=3, column=1)

        # ZAMAN ARALIĞI
        zaman_araligi_label = tk.Label(calisma_modu, text="Zaman (dk):")
        zaman_araligi_label.grid(row=4, column=0)
        self.zaman_araligi_entry = tk.Entry(calisma_modu)
        self.zaman_araligi_entry.grid(row=4, column=1)

        # ZAMAN ARALIĞI
        veri_oku_label = tk.Label(calisma_modu, text="Grafik Veri Yazdırma Aralığı (ms)")
        veri_oku_label.grid(row=5, column=0)
        self.veri_oku_entry = tk.Entry(calisma_modu)
        self.veri_oku_entry.grid(row=5, column=1)

        # Add buttons
        button_frame = tk.Frame(home_page)
        button_frame.pack(pady=10)

        iptal_button = tk.Button(button_frame, text="İptal", command=self.quit)
        iptal_button.pack(side="left", padx=5)

        kaydet_button = tk.Button(button_frame, text="Kaydet", command=self.save_settings)
        kaydet_button.pack(side="left", padx=5)

        kapat_button = tk.Button(button_frame, text="Kapat", command=self.quit)
        kapat_button.pack(side="left", padx=5)

    def save_settings(self):
        config = configparser.ConfigParser()

        # Ana sayfa verileri
        com_port = self.com_port_entry.get()
        baud_rate = self.baud_rate_combobox.get()
        esik_deger = self.esik_deger_entry.get()
        eksen_deger = self.eksen_deger_entry.get()
        zaman_araligi = self.zaman_araligi_entry.get()
        veri_oku = self.veri_oku_entry.get()

        # .ini dosyasına verileri yazma
        config['AnaSayfa'] = {
            'com port': com_port,
            'baud rate': baud_rate,
            'esik degeri': esik_deger,
            'eksen degeri': eksen_deger,
            'zaman araligi': zaman_araligi,
            'veri oku': veri_oku
        }

        with open('settings.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile) 

    def start_serial_reader(self):
        # Dosya yolunu burada doğru şekilde belirtin
        subprocess.Popen(['python', 'serial_read.py'])

if __name__ == '__main__':
    app = Arayuz()
    app.mainloop()
