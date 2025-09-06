#!/usr/bin/env python3
"""
Migrate data from MongoDB backend to PostgreSQL frontend
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_from_backend():
    """Migrate data from MongoDB backend to PostgreSQL frontend"""
    
    print("=== Backend MongoDB to Frontend PostgreSQL Migration ===")
    
    # MongoDB connection (your backend)
    mongodb_url = "mongodb://2.tcp.ngrok.io:10482"
    print(f"Connecting to MongoDB backend: {mongodb_url}")
    
    try:
        from pymongo import MongoClient
        
        # Connect with timeout
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✓ MongoDB backend connection successful")
        
        # Get database and collection
        db = client['flask_nosql_db']
        collection = db['data_collection']
        
        # Count documents
        count = collection.count_documents({})
        print(f"✓ Found {count} documents in backend")
        
        if count == 0:
            print("ℹ No data to migrate from backend")
            return True
        
        # Show sample data structure
        sample = collection.find_one()
        print(f"✓ Sample document structure: {list(sample.keys())}")
        
    except Exception as e:
        print(f"✗ MongoDB backend connection failed: {e}")
        print("ℹ This might be expected if the MongoDB server is slow/unavailable")
        return False
    
    # PostgreSQL frontend connection
    print(f"\nConnecting to PostgreSQL frontend...")
    
    try:
        from app import app, db
        from models import Item, Receipt
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            print("✓ PostgreSQL frontend tables ready")
            
            # Migration counters
            items_migrated = 0
            
            # Get all documents from MongoDB
            documents = collection.find()
            
            for doc in documents:
                try:
                    # Extract data from MongoDB document
                    # Assuming the document has receipt data structure
                    
                    # Create receipt
                    receipt_id = f"REC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{doc.get('_id', 'unknown')}"
                    
                    receipt = Receipt(
                        receipt_id=receipt_id,
                        store_name=doc.get('vendor') or doc.get('store_name'),
                        purchase_date=doc.get('date') or doc.get('purchase_date'),
                        total_amount=doc.get('total') or doc.get('total_amount'),
                        tax_amount=None
                    )
                    
                    db.session.add(receipt)
                    
                    # If the document has items, create them too
                    if 'items' in doc:
                        for item_data in doc['items']:
                            item = Item(
                                receipt_id=receipt_id,
                                product_name=item_data.get('productName', 'Unknown Product'),
                                purchase_date=doc.get('date') or datetime.now().date(),
                                expiration_date=item_data.get('expirationDate'),
                                price=float(item_data.get('price', 0.0))
                            )
                            db.session.add(item)
                            items_migrated += 1
                    
                    items_migrated += 1
                    
                except Exception as e:
                    print(f"  Error migrating document {doc.get('_id')}: {e}")
                    continue
            
            # Commit all changes
            db.session.commit()
            print(f"\n✓ Migration completed!")
            print(f"Items migrated: {items_migrated}")
            print(f"Receipts migrated: {receipts_migrated}")
            
            # Summary
            total_items = Item.query.count()
            total_receipts = Receipt.query.count()
            total_value = db.session.query(db.func.sum(Item.price)).scalar() or 0
            
            print(f"\n=== Migration Summary ===")
            print(f"Items migrated: {items_migrated}")
            print(f"Receipts migrated: {receipts_migrated}")
            print(f"Total items in PostgreSQL: {total_items}")
            print(f"Total receipts in PostgreSQL: {total_receipts}")
            print(f"Total value: ${total_value:.2f}")
            
            return True
            
    except Exception as e:
            print(f"✗ PostgreSQL migration failed: {e}")
            return False
    
    finally:
        if 'client' in locals():
            client.close()
            print("✓ MongoDB connection closed")

def main():
    """Main migration function"""
    print("Starting backend to frontend migration...")
    
    # Check if user wants to proceed
    response = input("This will copy data from MongoDB backend to PostgreSQL frontend. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    success = migrate_from_backend()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use the PostgreSQL frontend with your data.")
    else:
        print("\n❌ Migration failed. Check the errors above.")

if __name__ == '__main__':
    main()

