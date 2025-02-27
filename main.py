from fastapi import FastAPI
import logging
from openApi.services.amend_processing_service import process_tasks 
from logger.loggers import get_logger

app = FastAPI()

# Initialize logger
logger = get_logger(__name__)
                    
if __name__ == "__main__":
    logging.info("Starting task processing...")
    process_tasks()
    logging.info("Task processing completed.")