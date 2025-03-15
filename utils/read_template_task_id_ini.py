'''
read_template_task_id_ini.py file is as follows:

    Purpose: This script reads the TEMPLATE_TASK_ID from an INI file.
    Created Date: 2025-01-08
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2024-01-19
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: configparser, utils.loggers, utils.Custom_Exceptions
    Related Files: Case_controller.js
    Notes:
'''

import configparser
from utils.loggers import get_logger
from utils.Custom_Exceptions import INIFileReadError

logger = get_logger("amend_status_logger")

def read_template_task_id_ini():
    """
    Reads the TEMPLATE_TASK_ID from the INI file.
    Returns: (success, template_task_id or error)
    """
    file_path = "config/Set_Template_TaskID.ini"
    try:
        config = configparser.ConfigParser()
        config.read(file_path)
        
        if "TEMPLATE_TASK" in config and "TEMPLATE_TASK_ID" in config["TEMPLATE_TASK"]:
            template_task_id = config["TEMPLATE_TASK"]["TEMPLATE_TASK_ID"]
            logger.info(f"Read TEMPLATE_TASK_ID: {template_task_id} from {file_path}")
            return True, int(template_task_id)
        else:
            error_message = f"TEMPLATE_TASK_ID not found in {file_path}"
            logger.error(error_message)
            return False, error_message
    except Exception as ini_read_error:
        logger.error(f"Failed to read INI file {file_path}: {ini_read_error}")
        raise INIFileReadError(f"Failed to read INI file {file_path}: {ini_read_error}")

def get_template_task_id():
    """
    Gets the TEMPLATE_TASK_ID from the INI file and handles errors.
    Returns: (success, template_task_id or error)
    """
    success_read_ini, template_task_id = read_template_task_id_ini()
    if not success_read_ini:
        raise INIFileReadError(template_task_id)
    return template_task_id