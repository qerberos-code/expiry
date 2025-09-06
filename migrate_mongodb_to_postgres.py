#!/usr/bin/env python3
"""
Migration script to copy data from MongoDB to PostgreSQL
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_data():
    """Migrate data from MongoDB to PostgreSQL"""
    
    print("=== MongoDB to PostgreSQL Migration ===")
    
    # MongoDB connection
    mongodb_url = "mongodb://2.tcp.ngrok.io:10482"
    print(f"Connecting to MongoDB: {mongodb_url}")
    
    try:
        from pymongo import MongoClient
        client = MongoClient(mongodb_url)
        
        # Test connection
        client.admin.command('ping')
        print("✓ MongoDB connection successful")
        
        # Get database and collections
        db = client.get_default_database()
        print(f"Using database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False
    
    # PostgreSQL connection
    postgres_url = os.getenv('DATABASE_URL')
    if not postgres_url:
        postgres_url = 'sqlite:///expiry.db'
        print("Warning: DATABASE_URL not set, using SQLite fallback")
    
    print(f"Connecting to PostgreSQL: {postgres_url[:20]}...")
    
    try:
        from app import app, db
        from models import Item, Receipt
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            print("✓ PostgreSQL tables created/verified")
            
            # Migration counters
            items_migrated = 0
            receipts_migrated = 0
            
            # Migrate items
            if 'items' in collections:
                print("\n--- Migrating Items ---")
                items_collection = db['items']
                mongodb_items = items_collection.find()
                
                for item_doc in mongodb_items:
                    try:
                        # Map MongoDB document to PostgreSQL model
                        item = Item(
                            receipt_id=item_doc.get('receiptId'),
                            product_name=item_doc.get('productName', 'Unknown Product'),
                            purchase_date=item_doc.get('purchaseDate', datetime.now().date()),
                            expiration_date=item_doc.get('expirationDate'),
                            price=float(item_doc.get('price', 0.0))
                        )
                        
                        # Check if item already exists
                        existing = Item.query.filter_by(
                            product_name=item.product_name,
                            purchase_date=item.purchase_date,
                            price=item.price
                        ).first()
                        
                        if not existing:
                            db.session.add(item)
                            items_migrated += 1
                            print(f"  Migrated: {item.product_name}")
                        else:
                            print(f"  Skipped (exists): {item.product_name}")
                            
                    except Exception as e:
                        print(f"  Error migrating item {item_doc.get('_id')}: {e}")
                        continue
                
                print(f"✓ Items migrated: {items_migrated}")
            
            # Migrate receipts
            if 'receipts' in collections:
                print("\n--- Migrating Receipts ---")
                receipts_collection = db['receipts']
                mongodb_receipts = receipts_collection.find()
                
                for receipt_doc in mongodb_receipts:
                    try:
                        # Map MongoDB document to PostgreSQL model
                        receipt = Receipt(
                            receipt_id=receipt_doc.get('receiptId', f"REC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
                            store_name=receipt_doc.get('storeName'),
                            purchase_date=receipt_doc.get('purchaseDate'),
                            total_amount=receipt_doc.get('totalAmount'),
                            tax_amount=receipt_doc.get('taxAmount')
                        )
                        
                        # Check if receipt already exists
                        existing = Receipt.query.filter_by(receipt_id=receipt.receipt_id).first()
                        
                        if not existing:
                            db.session.add(receipt)
                            receipts_migrated += 1
                            print(f"  Migrated: {receipt.receipt_id}")
                        else:
                            print(f"  Skipped (exists): {receipt.receipt_id}")
                            
                    except Exception as e:
                        print(f"  Error migrating receipt {receipt_doc.get('_id')}: {e}")
                        continue
                
                print(f"✓ Receipts migrated: {receipts_migrated}")
            
            # Commit all changes
            db.session.commit()
            print("\n✓ All changes committed to PostgreSQL")
            
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
        # Close MongoDB connection
        if 'client' in locals():
            client.close()
            print("✓ MongoDB connection closed")

def main():
    """Main migration function"""
    print("Starting MongoDB to PostgreSQL migration...")
    
    # Check if user wants to proceed
    response = input("This will copy data from MongoDB to PostgreSQL. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    success = migrate_data()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use the PostgreSQL version of the app.")
    else:
        print("\n❌ Migration failed. Check the errors above.")

if __name__ == '__main__':
    main()
