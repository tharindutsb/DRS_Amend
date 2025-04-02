------------------------------------------------------------------------
Python Project File Structure
------------------------------------------------------------------------
# DRC Amend Task Processing System

This system automates the process of balancing resources (cases) between **DRCs (Data Resource Centers)** based on predefined rules. It ensures that resources are transferred from a **donor DRC** to a **receiver DRC** without violating resource thresholds, updates the database with the new resource distribution, and tracks the task status.

---

## **Table of Contents**
1. [Purpose](#purpose)
2. [Workflow](#workflow)
3. [Code Structure](#code-structure)
4. [Setup Instructions](#setup-instructions)
5. [Usage](#usage)
6. [Error Handling](#error-handling)
7. [Logging](#logging)
8. [Contributing](#contributing)
9. [License](#license)
10. [Created By](#created-by)

---

## **Purpose**
The purpose of this system is to:
- Automate the balancing of resources between DRCs.
- Ensure resource thresholds are not violated during transfers.
- Update the database with the new resource distribution.
- Track and update task statuses in the system.

---

## **Workflow**
The system follows a step-by-step workflow to process tasks:
1. Fetch an open task from the `System_tasks` collection.
2. Validate the task against the `Template_task` collection.
3. Fetch transaction details for the given batch ID.
4. Fetch cases associated with the batch ID.
5. Balance resources between the donor and receiver DRCs.
6. Update the case distribution collection with new DRC values.
7. Update the summary collection with new resource counts.
8. Mark the transaction as `closed`.
9. Update the task status to `completed`.

---

## **Code Structure**
The system is divided into the following modules:

### **1. `connectDB.py`**
- **Purpose**: Handles database connections and collection initialization.
- **Key Functions**:
  - `get_collection(collection_name)`: Returns a specific collection from the database.

---

### **2. `balance_resources.py`**
- **Purpose**: Implements the logic for balancing resources between DRCs.
- **Key Functions**:
  - `balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)`: Balances resources and returns updated DRC mappings.
    - **Steps**:
      1. **Initialize Resource Tracker**: Tracks resources by DRC and resource type.
      2. **Validate DRCs and Resource Type**:
         - Ensure `receiver_drc` and `donor_drc` exist.
         - Validate the existence of `rtom` in both DRCs.
      3. **Check Resource Thresholds**:
         - Ensure `donor_drc`'s resource count for `rtom` does not fall below 20% after transfer.
         - Ensure `receiver_drc`'s resource count for `rtom` does not fall below 20% after transfer.
      4. **Perform Resource Transfer**:
         - Transfer cases from `donor_drc` to `receiver_drc` for the specified `rtom`.
      5. **Balance Back Resources**:
         - Use a round-robin method to balance resources between DRCs for common resource types (excluding `rtom`).
      6. **Update Resource Mapping**:
         - Convert the updated resource tracker back to the original format and return the updated mappings.
      7. **Error Handling**:
         - Log errors and raise a `ResourceBalanceError` in case of exceptions.

---

### **3. `database_checks.py`**
- **Purpose**: Handles database queries and validations.
- **Key Functions**:
  - `update_task_status(system_task_collection, task_id, status, error_description=None)`: Updates the status of a task in the `System_tasks` collection.
  - `fetch_and_validate_template_task(template_task_collection, template_task_id, task_type)`: Fetches and validates a template task.
  - `fetch_transaction_details(transaction_collection, case_distribution_batch_id)`: Fetches transaction details for a batch ID.
  - `fetch_cases_for_batch(case_collection, case_distribution_batch_id)`: Fetches cases for a batch ID.

---

### **4. `update_databases.py`**
- **Purpose**: Updates the database after resource balancing.
- **Key Functions**:
  - `update_template_task_collection(case_distribution_batch_id)`: Updates the `Template_task` collection with the new `TEMPLATE_TASK_ID` and parameters.
  - `update_case_distribution_collection(case_collection, updated_drcs, existing_drcs)`: Updates the case distribution collection with new DRC values.
  - `rollback_case_distribution_collection(case_collection, original_states)`: Rolls back the case distribution collection to its original state.
  - `update_summary_in_mongo(summary_collection, transaction_collection, updated_drcs, case_distribution_batch_id)`: Updates the summary collection and marks the transaction as closed.
  - `rollback_summary_in_mongo(summary_collection, original_counts, case_distribution_batch_id)`: Rolls back the summary collection to its original state.

---

### **5. `task_processor.py`**
- **Purpose**: Processes tasks sequentially.
- **Key Functions**:
  - `check_template_task_in_system_tasks(template_task_id)`: Checks if the `TEMPLATE_TASK_ID` exists in the `System_tasks` collection.
  - `validate_template_task_parameters(system_task, template_task)`: Validates that the `Template_Task_Id`, `task_type`, and parameters match between the `System_tasks` and `Template_task` collections.
  - `process_single_batch(task)`: Processes a single batch task.
  - `amend_task_processing()`: Fetches and processes open tasks.

---

### **6. `read_template_task_id_ini.py`**
- **Purpose**: Reads the `TEMPLATE_TASK_ID` from an INI file.
- **Key Functions**:
  - `read_template_task_id_ini()`: Reads the `TEMPLATE_TASK_ID` from the INI file.
  - `get_template_task_id()`: Gets the `TEMPLATE_TASK_ID` from the INI file and handles errors.

---

### **7. `main.py`**
- **Purpose**: Entry point of the application.
- **Key Functionality**:
  - Calls `amend_task_processing()` to start task processing.

---

## **Setup Instructions**
1. **Prerequisites**:
   - Python 3.8 or higher.
   - MongoDB installed and running.
   - Required Python packages: `pymongo`, `configparser`.

2. **Install Dependencies**:
   ```bash
   pip install pymongo configparser
   ```

3. **Configuration**:
   - Ensure the MongoDB connection details are correctly set in the `connectDB.py` file.
   - Update the `config/Set_Template_TaskID.ini` file with the correct `TEMPLATE_TASK_ID`.

---

## **Usage**
1. **Run the main script**:
   ```bash
   python main.py
   ```

2. **Monitor the logs**:
   - Logs are generated in the `logs` directory.
   - Check the logs for any errors or status updates.

---

## **Error Handling**
- The system includes custom exceptions to handle various error scenarios.
- Errors are logged using the `utils.loggers` module.
- In case of errors, the system attempts to rollback changes to maintain data consistency.

---

## **Logging**
- The system uses a custom logging module (`utils.loggers`) to log information, warnings, and errors.
- Logs are stored in the `logs` directory with timestamps.

---

## **Contributing**
- Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

## **License**
- This project is licensed under the SLT.

---

## **Created By**
- **T.S.Balasooriya**: (tharindutsb@gmail.com)  
- **A.A.P.Bathiya**: (pasanbathiya246@gmail.com)  
- **Amupama Maheepala**: (anupamamaheepala999@gmail.com)