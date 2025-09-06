#!/usr/bin/env python3
"""
Test MongoDB connection and explore data structure
"""

import sys
from datetime import datetime

def test_mongodb():
    """Test MongoDB connection and explore data"""
    
    mongodb_url = "mongodb://2.tcp.ngrok.io:10482"
    print(f"Testing MongoDB connection: {mongodb_url}")
    
    try:
        from pymongo import MongoClient
        client = MongoClient(mongodb_url)
        
        # Test connection
        client.admin.command('ping')
        print("✓ MongoDB connection successful")
        
        # Get database
        db = client.get_default_database()
        print(f"Database name: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
        
        # Explore items collection
        if 'items' in collections:
            print("\n--- Items Collection ---")
            items_collection = db['items']
            count = items_collection.count_documents({})
            print(f"Total items: {count}")
            
            # Show sample documents
            sample_items = items_collection.find().limit(3)
            for i, item in enumerate(sample_items, 1):
                print(f"\nSample Item {i}:")
                print(f"  _id: {item.get('_id')}")
                print(f"  productName: {item.get('productName')}")
                print(f"  purchaseDate: {item.get('purchaseDate')}")
                print(f"  expirationDate: {item.get('expirationDate')}")
                print(f"  price: {item.get('price')}")
                print(f"  receiptId: {item.get('receiptId')}")
        
        # Explore receipts collection
        if 'receipts' in collections:
            print("\n--- Receipts Collection ---")
            receipts_collection = db['receipts']
            count = receipts_collection.count_documents({})
            print(f"Total receipts: {count}")
            
            # Show sample documents
            sample_receipts = receipts_collection.find().limit(2)
            for i, receipt in enumerate(sample_receipts, 1):
                print(f"\nSample Receipt {i}:")
                print(f"  _id: {receipt.get('_id')}")
                print(f"  receiptId: {receipt.get('receiptId')}")
                print(f"  storeName: {receipt.get('storeName')}")
                print(f"  purchaseDate: {receipt.get('purchaseDate')}")
                print(f"  totalAmount: {receipt.get('totalAmount')}")
                print(f"  taxAmount: {receipt.get('taxAmount')}")
        
        return True
        
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False
    
    finally:
        if 'client' in locals():
            client.close()
            print("\n✓ MongoDB connection closed")

if __name__ == '__main__':
    test_mongodb()
