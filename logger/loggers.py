import logging
import logging.config
import os

from Config.filePaths.filePath import get_filePath





# Ensure correct path for logging configuration
config_file = os.path.join(os.path.dirname(__file__), "loggers.ini")
logging.config.fileConfig(config_file, disable_existing_loggers=False)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
