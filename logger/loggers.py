import logging
import logging.config

# Load logger configuration from the ini file
config_file = 'logger/loggers.ini'
logging.config.fileConfig(config_file)

# Get loggers by their names
logger = logging.getLogger('name1')
logger = logging.getLogger('name2')

# # Example logging
# logger.info("This is an info message from logger_name1")
# logger.info("This is an info message from logger_name2")

def get_logger(name: str) -> logging.getLogger:
    """
    Get a logger by its name.
    """
    return logging.getLogger(name)

