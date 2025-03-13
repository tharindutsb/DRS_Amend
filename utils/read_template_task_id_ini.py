import configparser
from utils.loggers import get_logger

logger = get_logger("amend_status_logger")

def read_template_task_id_ini(file_path):
    """
    Reads the TEMPLATE_TASK_ID from the INI file.
    Returns: (success, template_task_id or error)
    """
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
    except Exception as e:
        logger.error(f"Failed to read INI file {file_path}: {e}")
        return False, str(e)