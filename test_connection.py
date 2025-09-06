#!/usr/bin/env python3
"""
Quick test of MongoDB connection
"""

def test_connection():
    try:
        from pymongo import MongoClient
        
        print("Testing MongoDB connection...")
        client = MongoClient('mongodb://2.tcp.ngrok.io:10482', serverSelectionTimeoutMS=5000)
        
        # Test connection with timeout
        client.admin.command('ping')
        print("✓ Connection successful!")
        
        # Get database info
        db = client['flask_nosql_db']
        collection = db['data_collection']
        
        # Count documents
        count = collection.count_documents({})
        print(f"✓ Found {count} documents in data_collection")
        
        # Show sample data
        if count > 0:
            sample = collection.find_one()
            print(f"✓ Sample document keys: {list(sample.keys())}")
        else:
            print("ℹ No documents found in collection")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == '__main__':
    test_connection()

