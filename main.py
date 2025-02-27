from fastapi import FastAPI
from openApi.services.amend_processing_service import process_tasks 
from logger.loggers import get_logger



# Initialize logger
logger = get_logger('name1,name2')
                    
if __name__ == "__main__":
    logger.info("Starting task processing...")
    process_tasks()
    logger.info("Task processing completed.")