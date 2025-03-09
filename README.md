------------------------------------------------------------------------
Python Project File Structure
------------------------------------------------------------------------
# DRC Amend Task Processing System

This system automates the process of balancing resources (cases) between **DRCs (Data Resource Centers)** based on predefined rules. It ensures that resources are transferred from a **donor DRC** to a **receiver DRC** without violating resource thresholds, updates the database with the new resource distribution, and tracks the task status.

---

## Table of Contents
1. [Purpose](#purpose)
2. [Workflow](#workflow)
3. [Code Structure](#code-structure)
4. [Setup Instructions](#setup-instructions)
5. [Usage](#usage)
6. [Error Handling](#error-handling)
7. [Logging](#logging)
8. [Contributing](#contributing)
9. [License](#license)

---

## Purpose
The purpose of this system is to:
- Automate the balancing of resources between DRCs.
- Ensure resource thresholds are not violated during transfers.
- Update the database with the new resource distribution.
- Track and update task statuses in the system.

---

## Workflow
The system follows a step-by-step workflow to process tasks:
1. Fetch an open task from the `System_tasks` collection.
2. Validate the task against the `Template_task` collection.
3. Fetch transaction details for the given batch ID.
4. Fetch cases associated with the batch ID.
5. Balance resources between the donor and receiver DRCs.
6. Update the case distribution collection with new DRC values.
7. Update the summary collection with new resource counts.
8. Mark the transaction as `close`.
9. Update the task status to `completed`.

---

## Code Structure
The system is divided into the following modules:

### `connectDB.py`
- Handles database connections and collection initialization.
- Functions:
  - `get_db_connection()`: Establishes a connection to MongoDB.
  - `get_collection(collection_name)`: Returns a specific collection from the database.

### `balance_resources.py`
- Implements the logic for balancing resources between DRCs.
- Functions:
  - `balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)`: Balances resources and returns updated DRC mappings.

### `database_checks.py`
- Handles database queries and validations.
- Functions:
  - `update_task_status()`: Updates the status of a task in the `System_tasks` collection.
  - `fetch_and_validate_template_task()`: Fetches and validates a template task.
  - `fetch_transaction_details()`: Fetches transaction details for a batch ID.
  - `fetch_cases_for_batch()`: Fetches cases for a batch ID.

### `update_databases.py`
- Updates the database after resource balancing.
- Functions:
  - `update_case_distribution_collection()`: Updates the case distribution collection with new DRC values.
  - `update_summary_in_mongo()`: Updates the summary collection and marks the transaction as closed.

### `task_processor.py`
- Processes tasks sequentially.
- Functions:
  - `process_single_batch()`: Processes a single batch task.
  - `amend_task_processing()`: Fetches and processes open tasks.

### `main.py`
- Entry point of the application.
- Calls `amend_task_processing()` to start task processing.

---

## Setup Instructions
1. **Prerequisites**:
   - Python 3.8 or higher.
   - MongoDB installed and running.
   - Required Python packages: `pymongo`, `configparser`.

2. **Install Dependencies**:
   ```bash
   pip install pymongo configparser
