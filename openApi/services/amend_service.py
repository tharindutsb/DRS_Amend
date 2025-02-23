from get_amend_plan import get_amend_plan
from balance_resources import balance_resources

def amend_resources(amend_request):
    """
    Handles the amendment request by fetching data from MongoDB, balancing resources, and updating MongoDB.
    
    :param amend_request: The amendment request containing rtom, donor_drc_id, receiver_drc_id, and transfer_count.
    :return: Updated DRCs with case IDs after balancing.
    """
    try:
        # Fetch data from MongoDB and get the amendment plan
        drcs, receiver_drc, donor_drc, rtom, transfer_value = get_amend_plan()

        # Perform the balance operation
        updated_drcs = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)

        return updated_drcs
    except Exception as e:
        print(f"Error in amend_resources: {e}")
        raise e