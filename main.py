from actionManipulation.task_processor import amend_task_processing
from logger.loggers import get_logger

# Initialize logger
logger = get_logger("task_status_logger")

if __name__ == "__main__":
    logger.info("Starting task processing...")
    amend_task_processing()
    logger.info("Task processing completed.")