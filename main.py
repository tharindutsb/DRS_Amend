from fastapi import FastAPI
import logging
from openApi.services.amend_processing_service import process_tasks 
from logger.loggers import get_logger



app = FastAPI()

# Initialize logger
logger = get_logger(__name__)
                    
if __name__ == "__main__":
    logger.info("Starting task processing...")
    process_tasks()
    logger.info("Task processing completed.")