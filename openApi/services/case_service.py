from pymongo import MongoClient
import datetime
from utils.DB_Config import CASE_COLLECTION, TRANSACTION_COLLECTION
from utils.connectDB import get_db_connection

db = get_db_connection()

def get_latest_batch_seq():
    try:
        last_record = db[TRANSACTION_COLLECTION].find_one({}, sort=[("batch_seq", -1)])
        return last_record["batch_seq"] + 1 if last_record else 1
    except Exception as e:
        print(f"❌ Error fetching batch_seq: {e}")
        return None

def add_amendment_record(amendment_data):
    try:
        batch_seq = get_latest_batch_seq()
        if batch_seq is None:
            return {"error": "Failed to fetch batch_seq"}

        amendment_data["batch_seq"] = batch_seq
        amendment_data["created_dtm"] = datetime.datetime.utcnow()

        db[TRANSACTION_COLLECTION].insert_one(amendment_data)
        return {"message": "✅ Amendment record added successfully", "batch_seq": batch_seq}
    except Exception as e:
        return {"error": f"❌ Database error: {str(e)}"}
