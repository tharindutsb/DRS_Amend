'''
amend_task_processing  main.py file is as follows:

    Purpose: This template is used for the DRC Amend.
    Created Date: 2025-01-08
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2024-01-19
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Node.js v20.11.1
    Dependencies: express
    Related Files: Case_controller.js
    Notes:  
'''


from actionManipulation.task_processor import amend_task_processing
from logger.loggers import get_logger

# Initialize logger
logger = get_logger("task_status_logger")

if __name__ == "__main__":
    logger.info("Starting task processing...")
    amend_task_processing()
    logger.info("Task processing completed.")

