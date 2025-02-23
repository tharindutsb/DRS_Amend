from logging.handlers import TimedRotatingFileHandler
import os
import zipfile
from datetime import datetime


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when, interval, backupCount, backup_dir, **kwargs):
        super().__init__(filename, when, interval, backupCount, **kwargs)
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def doRollover(self):
        # Perform normal rollover
        super().doRollover()

        # Move old logs to the backup directory and compress them
        zip_name = os.path.join(self.backup_dir, f"logs_backup_{datetime.now().strftime('%Y-%m')}.zip")
        with zipfile.ZipFile(zip_name, "a", zipfile.ZIP_DEFLATED) as zipf:
            for log_file in os.listdir(os.path.dirname(self.baseFilename)):
                if log_file.startswith(os.path.basename(self.baseFilename)) and log_file != os.path.basename(self.baseFilename):
                    src = os.path.join(os.path.dirname(self.baseFilename), log_file)
                    zipf.write(src, os.path.basename(src))
                    os.remove(src)

