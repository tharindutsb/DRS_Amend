from actionManipulationCopy.task_processor import process_tasks 
from logger.loggers import get_logger

# Initialize logger
logger = get_logger("task_status_logger")
                    
if __name__ == "__main__":
    logger.info("Starting task processing...")
    process_tasks()
    logger.info("Task processing completed.")
