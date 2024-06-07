import os

class DataWriter:
    def __init__(self):
        self.filename = 'data.txt'
        self.max_entries = 300
        self.entries = 0

        # Dosya varsa mevcut satır sayısını hesapla
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.entries = len(file.readlines())

    def write_data(self, data):
        try:
            with open(self.filename, 'a') as file:
                file.write(data + '\n')
            self.entries += 1

            if self.entries >= self.max_entries:
                self.clear_file()

        except Exception as e:
            print(f"Dosya yazma hatası: {e}")

    def clear_file(self):
        try:
            with open(self.filename, 'w') as file:
                file.truncate(0)
            self.entries = 0
        except Exception as e:
            print(f"Dosya temizleme hatası: {e}")
