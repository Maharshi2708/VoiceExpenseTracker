import requests
import logging
from config.config import AIRTABLE_BASE_ID, AIRTABLE_API_KEY, AIRTABLE_TABLE_NAME

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def store_expense(data):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    fields = {
        "fields": {
            "Amount": data.get("amount", 0),
            "Category": data.get("category", "Miscellaneous"),
            "SubCategory": data.get("sub_category", ""),
            "Description": data.get("description", "")
        }
    }
    
    logger.info(f"Sending to Airtable: {fields}")
    
    try:
        response = requests.post(url, json=fields, headers=headers)
        
        logger.info(f"Airtable response status: {response.status_code}")
        logger.debug(f"Airtable response content: {response.text}")
        
        if response.status_code == 200:
            logger.info("Record added successfully!")
            return True
        else:
            logger.error(f"Failed to add record: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception when storing expense: {str(e)}")
        return False