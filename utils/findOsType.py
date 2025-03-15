'''
findOsType.py file is as follows:

    Purpose: This script determines the operating system type.
    Created Date: 2025-03-01
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2025-03-15
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: platform
    Notes:
'''

import platform

def find_os_type():
    """
    Determine the operating system type.
    """
    os_type = platform.system()
    return os_type

# Example usage
if __name__ == "__main__":
    os_type = find_os_type()
    print(f"Operating System Type: {os_type}")
