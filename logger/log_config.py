# import logging
# from loguru import logger

# logger.add("application.log", rotation="500 MB", compression="zip", level="INFO")

# # Optionally, you can add custom handlers here, for instance, to send logs to a file, database, or monitoring system.


import logging

# Define log file location
LOG_FILE = "application.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to INFO to reduce unnecessary debug logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger("intern_app")  # Use a consistent logger name

logger.info("Logging system initialized successfully!")
