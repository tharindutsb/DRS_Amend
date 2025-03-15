'''
balance_resources.py file is as follows:

    Purpose: This script balances resources between DRCs based on the given logic.
    Created Date: 2025-03-01
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2025-03-15
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: collections, utils.loggers, utils.Custom_Exceptions
    Notes: 
        - The script first checks if the receiver and donor DRCs exist.
        - It then verifies if the resource (rtom) exists in both DRCs.
        - The donor DRC's resources are checked to ensure they do not fall below 20% after the transfer.
        - Similarly, the receiver DRC's resources are checked to ensure they do not fall below 20% after the transfer.
        - The transfer is performed by moving the specified number of cases from the donor to the receiver.
        - A round-robin method is used to balance back the resources, excluding the rtom.
'''

# balance_resources.py
from collections import defaultdict
from utils.loggers import get_logger
from utils.Custom_Exceptions import ResourceBalanceError

logger = get_logger("amend_status_logger")

def balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value):
    """
    Balances resources between DRCs based on the given logic.
    Returns: (success, updated_drcs or error_message)
    """
    resource_tracker = defaultdict(lambda: defaultdict(list))
    for case_id, (drc, resource) in drcs.items():
        resource_tracker[drc][resource].append(case_id)

    try:
        # Step 1: Check if receiver_drc and donor_drc exist
        if receiver_drc not in resource_tracker or donor_drc not in resource_tracker:
            logger.error(f"One of the DRCs ({receiver_drc} or {donor_drc}) does not exist.")
            return False, f"One of the DRCs ({receiver_drc} or {donor_drc}) does not exist."

        # Step 2: Check if rtom exists in both receiver_drc and donor_drc
        if rtom not in resource_tracker[receiver_drc] or rtom not in resource_tracker[donor_drc]:
            logger.error(f"The resource {rtom} does not exist in both {receiver_drc} and {donor_drc}.")
            return False, f"The resource {rtom} does not exist in both {receiver_drc} and {donor_drc}."

        # Step 3: Check if donor_drc can donate without going below 20% of its resources
        donor_resource_count = len(resource_tracker[donor_drc][rtom])
        if donor_resource_count > 0 and (donor_resource_count - transfer_value < 0.2 * donor_resource_count):
            logger.error(f"Insufficient resources in {donor_drc} for the Donate.")
            return False, f"Insufficient resources in {donor_drc} for the Donate."

        # Step 4: Check if receiver_drc can receive without going below 20% of its resources
        receiver_resource_count = len(resource_tracker[receiver_drc][rtom])
        if receiver_resource_count > 0 and (receiver_resource_count - transfer_value < 0.2 * receiver_resource_count):
            logger.error(f"Insufficient resources in {receiver_drc} for the Balance.")
            return False, f"Insufficient resources in {receiver_drc} for the Balance."

        # Step 5: Perform the transfer
        for _ in range(transfer_value):
            case_id = resource_tracker[donor_drc][rtom].pop(0)
            resource_tracker[receiver_drc][rtom].append(case_id)

        # Step 6: Balance back using round-robin method
        common_resources = set(resource_tracker[receiver_drc].keys()).intersection(set(resource_tracker[donor_drc].keys()))
        common_resources.discard(rtom)  # Exclude the rtom from balancing back

        sorted_resources = sorted(common_resources, key=lambda x: len(resource_tracker[receiver_drc][x]), reverse=True)

        remaining_value = transfer_value
        index = 0
        while remaining_value > 0:
            resource = sorted_resources[index % len(sorted_resources)]
            if len(resource_tracker[receiver_drc][resource]) >= 1:
                case_id = resource_tracker[receiver_drc][resource].pop(0)
                resource_tracker[donor_drc][resource].append(case_id)
                remaining_value -= 1
            index += 1

        # Convert resource_tracker back to the original drcs format
        updated_drcs = {}
        for drc, resources in resource_tracker.items():
            for resource, case_ids in resources.items():
                for case_id in case_ids:
                    updated_drcs[case_id] = [drc, resource]

        return True, updated_drcs  # Success
    except Exception as balance_error:
        logger.error(f"Error balancing resources: {balance_error}")
        raise ResourceBalanceError(f"Error balancing resources: {balance_error}")