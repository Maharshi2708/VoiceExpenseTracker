import re
import logging

logger = logging.getLogger(__name__)

def parse_expense_message(message_text):
    logger.info(f"Parsing expense message: {message_text}")
    
    data = {
        "amount": 0,
        "category": "Miscellaneous",
        "sub_category": "",
        "description": message_text
    }
    
    amount_pattern = r'(?:rs\.?|₹|inr|rupees?|\$)?\s*(\d+(?:\.\d+)?)'
    amount_match = re.search(amount_pattern, message_text, re.IGNORECASE)
    
    if amount_match:
        try:
            data["amount"] = float(amount_match.group(1))
            logger.info(f"Found amount: {data['amount']}")
        except (ValueError, IndexError):
            logger.warning("Failed to extract amount")
    
    category_patterns = [
        r'(?:for|on|in|category:?)\s+([a-zA-Z\s]+)',
        r'([a-zA-Z]+)\s+(?:expense|purchase|payment)'
    ]
    
    for pattern in category_patterns:
        category_match = re.search(pattern, message_text, re.IGNORECASE)
        if category_match:
            data["category"] = category_match.group(1).strip().capitalize()
            logger.info(f"Found category: {data['category']}")
            break
    
    subcategory_pattern = r'(?:subcategory:?|sub:?|type:?)\s+([a-zA-Z\s]+)'
    subcategory_match = re.search(subcategory_pattern, message_text, re.IGNORECASE)
    
    if subcategory_match:
        data["sub_category"] = subcategory_match.group(1).strip().capitalize()
        logger.info(f"Found subcategory: {data['sub_category']}")
    description = message_text
    logger.info(f"Final parsed data: {data}")
    return data

def is_expense_message(message_text):
    expense_indicators = [
        r'(?:rs\.?|₹|inr|rupees?|\$)\s*\d+',  
        r'\d+\s*(?:rs\.?|₹|inr|rupees?|\$)',  
        r'spent',
        r'paid',
        r'expense',
        r'bought',
        r'purchased'
    ]
    
    for pattern in expense_indicators:
        if re.search(pattern, message_text, re.IGNORECASE):
            return True
    
    return False