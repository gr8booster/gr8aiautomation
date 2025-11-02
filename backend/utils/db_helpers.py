"""
Database helper functions
"""
from typing import Optional, List, Dict, Any

def serialize_doc(doc: Optional[Dict]) -> Optional[Dict]:
    """Convert MongoDB ObjectId to string"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def serialize_docs(docs: List[Dict]) -> List[Dict]:
    """Convert list of MongoDB documents"""
    return [serialize_doc(doc) for doc in docs]
