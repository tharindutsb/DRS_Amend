
from logger.loggers import get_logger

# Example usage of the logger
def example_usage():
    # Get the logger
    logger = get_logger("app_loggers")

    # Log messages at different levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

if __name__ == "__main__":
    example_usage()