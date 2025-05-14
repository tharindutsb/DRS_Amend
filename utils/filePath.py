'''
filePath.py file is as follows:

    Purpose: This script retrieves file paths based on the operating system.
    Created Date: 2025-03-01
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2025-03-15
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: configparser, platform
    Notes:
'''

import configparser
import platform
from pathlib import Path
import logging
 
def get_project_root():
    """
    Returns the project root directory dynamically.
    Assumes this script is inside the project directory.
    """
    return Path(__file__).resolve().parent.parent  # Adjusted depth to match the actual project structure


def get_filePath(key):
    try:
       
        logger = logging.getLogger("System_logger")
        logging.basicConfig(level=logging.INFO)  # Configure logging if not already set

        # Initialize ConfigParser
        config = configparser.ConfigParser()

        # Get the project root dynamically
        project_root = get_project_root()

        # Construct the config file path
        config_file_path = project_root / "config" / "filePaths.ini"  # Ensure the path matches the actual directory structure

        if not config_file_path.is_file():
            raise FileNotFoundError(f"Configuration file '{config_file_path}' not found.")

        config.read(str(config_file_path))  # Ensure path is read as a string

        # Determine the operating system
        os_type = platform.system().lower()  # 'windows' or 'linux'

        # Map OS type to key suffix
        os_suffix = "WIN" if os_type == 'windows' else "LIN"

        # Define section mappings
        section_mapping = {
            "loggers": "loggersFile_Path",
            "DB_Config": "DB_ConfigFile_Path",
            "filePaths": "FilePathConfigFile_path",
            "Set_Template_TaskID": "Set_Template_TaskIDFile_Path",
        }

        # Retrieve section name
        section = section_mapping.get(key)
        if not section:
            raise KeyError(f"Key '{key}' does not have a mapped section.")

        # Retrieve the path
        if section in config:
            requested_key = f"{os_suffix}_CONFIG"  # Corrected key suffix to match the INI file structure
            path = config[section].get(requested_key, "").strip()

            if not path:
                logger.error(f"Key '{requested_key}' not found in section '{section}'.")
                return False  # Return False if the key is missing

            return Path(path)  # Return as Path object for consistency

        else:
            logger.error(f"Section '{section}' is missing in the configuration file.")
            return False  # Return False if the section is missing

    except FileNotFoundError as fnf_error:
        logger.error(f"Error: {fnf_error}")
        return False  
    except KeyError as key_error:
        logger.error(f"Error: {key_error}")
        return False  
    except Exception as e:
        logger.error(f"Error: Unexpected error occurred - {e}")
        return False 
