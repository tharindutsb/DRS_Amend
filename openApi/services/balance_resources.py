from collections import defaultdict
from openApi.services.update_amend_drcs import update_drcs_in_mongo

from logger.loggers import get_logger

logger = get_logger(__name__)


def balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value):
    """
    Balances resources between DRCs based on the given logic, ensuring only one resource is balanced at a time.
    
    :param drcs: Dictionary of case IDs mapping to DRC and resource pairs.
    :param receiver_drc: The DRC receiving resources (e.g., 'D1').
    :param donor_drc: The DRC donating resources (e.g., 'D2').
    :param rtom: The resource to modify (e.g., 'R1').
    :param transfer_value: The value to transfer between resources.
    :return: Updated DRCs with case IDs after balancing.
        
                    D1:
                        CW: [4, 3, 1, 9, 11, 15, 17, 19]
                        AG: [2, 13]
                    D2:
                        AG: [8, 6, 10, 14, 18]
                        CW: [7, 12, 20]
                        AD: [5, 16]
                        Error: Insufficient resources in D2 for the Balance.
    
    """
            
    # Convert drcs to a format that tracks resources and their case IDs
    resource_tracker = defaultdict(lambda: defaultdict(list))
    for case_id, (drc, resource) in drcs.items():
        resource_tracker[drc][resource].append(case_id)

    # Log initial state
    logger.debug("Initial DRCs with Case IDs:")
    for drc, resources in resource_tracker.items():
        logger.debug(f"{drc}:")
        for resource, case_ids in resources.items():
            logger.debug(f"  {resource}: {case_ids}")


    try:
        # Step 1: Check if receiver_drc and donor_drc exist
        if receiver_drc not in resource_tracker or donor_drc not in resource_tracker:
            raise ValueError(f"One of the DRCs ({receiver_drc} or {donor_drc}) does not exist in the resources dictionary.")
        
        # Step 2: Check if rtom exists in both receiver_drc and donor_drc
        if rtom not in resource_tracker[receiver_drc] or rtom not in resource_tracker[donor_drc]:
            raise ValueError(f"The resource {rtom} does not exist in both {receiver_drc} and {donor_drc}.")
        
        # Step 3: Check if donor_drc can donate without going below 20% of its resources
        donor_resource_count = len(resource_tracker[donor_drc][rtom])
        if donor_resource_count > 0 and (donor_resource_count - transfer_value < 0.2 * donor_resource_count):
            raise ValueError(f"Insufficient resources in {donor_drc} for the Donate.")
        
        # Step 4: Check if receiver_drc can receive without going below 20% of its resources
        receiver_resource_count = len(resource_tracker[receiver_drc][rtom])
        if receiver_resource_count > 0 and (receiver_resource_count - transfer_value < 0.2 * receiver_resource_count):
            raise ValueError(f"Insufficient resources in {receiver_drc} for the Balance.")

        # Step 5: Perform the transfer
        for _ in range(transfer_value):
            # Move a case ID from donor_drc to receiver_drc
            case_id = resource_tracker[donor_drc][rtom].pop(0)
            resource_tracker[receiver_drc][rtom].append(case_id)
        
        # Step 6: Balance back using round-robin method
        common_resources = set(resource_tracker[receiver_drc].keys()).intersection(set(resource_tracker[donor_drc].keys()))
        common_resources.discard(rtom)  # Exclude the rtom from balancing back
        
        # Sort common resources in descending order of their case counts in receiver_drc
        sorted_resources = sorted(common_resources, key=lambda x: len(resource_tracker[receiver_drc][x]), reverse=True)
        
        # Distribute the transfer_value using round-robin
        remaining_value = transfer_value
        index = 0  # Start with the first resource in the sorted list
        while remaining_value > 0:
            resource = sorted_resources[index % len(sorted_resources)]  # Cycle through resources
            if len(resource_tracker[receiver_drc][resource]) >= 1:
                # Move a case ID from receiver_drc to donor_drc
                case_id = resource_tracker[receiver_drc][resource].pop(0)
                resource_tracker[donor_drc][resource].append(case_id)
                remaining_value -= 1
            index += 1  # Move to the next resource in the round-robin cycle

        # Log final balanced state
        logger.debug(f"Balanced DRCs with Case IDs (Transfer Value = {transfer_value}):")
        for drc, resources in resource_tracker.items():
            logger.debug(f"{drc}:")
            for resource, case_ids in resources.items():
                logger.debug(f"  {resource}: {case_ids}")

        # Convert resource_tracker back to the original drcs format
        updated_drcs = {}
        for drc, resources in resource_tracker.items():
            for resource, case_ids in resources.items():
                for case_id in case_ids:
                    updated_drcs[case_id] = [drc, resource]
        
        # Log the final updated drcs dictionary
        logger.debug("Final Updated DRCs with Case IDs:")
        for case_id, (drc, resource) in updated_drcs.items():
            logger.debug(f"{case_id}: [{drc}, {resource}]")


        # If successful, update MongoDB with success status
        amend_description = f"Successfully transferred {transfer_value} cases of {rtom} from {donor_drc} to {receiver_drc}."
        update_drcs_in_mongo(updated_drcs, "Successful", amend_description)
        return updated_drcs

    except ValueError as e:
        # If an error occurs, update MongoDB with failure status and error message
        logger.error(f"Resource balancing failed: {str(e)}", exc_info=True)

        update_drcs_in_mongo(drcs, "Failed", str(e))
        return drcs
