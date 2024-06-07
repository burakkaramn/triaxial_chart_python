import os
from datetime import datetime, timedelta

class DataLogger:
    def __init__(self, log_directory='data_log', interval_minutes=10):
        self.log_directory = log_directory
        self.interval_minutes = interval_minutes
        self.current_log_file = None
        self.current_log_path = None
        self.next_log_time = None
        self._initialize_log_directory()
        self._update_log_file()

    def _initialize_log_directory(self):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def _get_next_log_time(self, now):
        next_minute = (now.minute // self.interval_minutes + 1) * self.interval_minutes
        next_log_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_minute)
        return next_log_time

    def _update_log_file(self):
        now = datetime.now()
        if self.next_log_time is None or now >= self.next_log_time:
            if self.current_log_file is not None:
                self.current_log_file.close()

            log_filename = now.strftime('%H_%M_%d_%m_%Y.txt')
            self.current_log_path = os.path.join(self.log_directory, log_filename)
            self.current_log_file = open(self.current_log_path, 'a')
            self.next_log_time = self._get_next_log_time(now)

    def log_data(self, data):
        self._update_log_file()
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.current_log_file.write(f"{timestamp} {data}\n")
        self.current_log_file.flush()

    def close(self):
        if self.current_log_file is not None:
            self.current_log_file.close()

# Örnek kullanım:
# logger = DataLogger(interval_minutes=10)
# logger.log_data("Test data")
# logger.close()
