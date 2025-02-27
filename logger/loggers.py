import logging
import logging.config
import os

# Ensure the logs directory exists
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Load logger configuration from loggers.ini
config_file = os.path.join(os.path.dirname(__file__), "../Config/logger/loggers.ini")
print(config_file)
logging.config.fileConfig(config_file)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

