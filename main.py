from actionManipulationCopy.task_processor import process_tasks
from utils.connectDB import get_db_connection, initialize_collections
from logger.loggers import get_logger

# Initialize logger
logger = get_logger("task_status_logger")

if __name__ == "__main__":
    logger.info("Starting task processing...")

    # Establish MongoDB connection
    db = get_db_connection()
    if db is None:
        logger.error("Database connection failed. Exiting...")
        exit(1)

    # Initialize collections
    collections = initialize_collections(db)
    
    # Pass the required collections to process_tasks
    process_tasks(
        collections["case_collection"],
        collections["transaction_collection"],
        collections["summary_collection"],
        collections["system_task_collection"],
        collections["template_task_collection"]
    )

    logger.info("Task processing completed.")
