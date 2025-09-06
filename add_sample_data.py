#!/usr/bin/env python3
"""
Add sample data to PostgreSQL frontend
Since MongoDB connection is slow, let's add some sample data to test the frontend
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_sample_data():
    """Add sample data to PostgreSQL frontend"""
    
    print("=== Adding Sample Data to PostgreSQL Frontend ===")
    
    try:
        from app import app, db
        from models import Item, Receipt
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            print("✓ PostgreSQL tables ready")
            
            # Check if we already have data
            existing_items = Item.query.count()
            if existing_items > 0:
                print(f"ℹ Found {existing_items} existing items")
                response = input("Add more sample data anyway? (y/N): ")
                if response.lower() != 'y':
                    print("Sample data addition cancelled.")
                    return
            
            # Add sample receipts
            sample_receipts = [
                {
                    'receipt_id': 'REC-2024-001',
                    'store_name': 'Safeway',
                    'purchase_date': datetime.now().date() - timedelta(days=2),
                    'total_amount': 72.91,
                    'tax_amount': 0.58
                },
                {
                    'receipt_id': 'REC-2024-002',
                    'store_name': 'Whole Foods',
                    'purchase_date': datetime.now().date() - timedelta(days=1),
                    'total_amount': 45.67,
                    'tax_amount': 3.65
                }
            ]
            
            # Add sample items
            sample_items = [
                # Receipt 1 items
                {
                    'receipt_id': 'REC-2024-001',
                    'product_name': 'Organic Milk',
                    'purchase_date': datetime.now().date() - timedelta(days=2),
                    'expiration_date': datetime.now().date() + timedelta(days=5),
                    'price': 4.99
                },
                {
                    'receipt_id': 'REC-2024-001',
                    'product_name': 'Whole Wheat Bread',
                    'purchase_date': datetime.now().date() - timedelta(days=2),
                    'expiration_date': datetime.now().date() + timedelta(days=4),
                    'price': 2.49
                },
                {
                    'receipt_id': 'REC-2024-001',
                    'product_name': 'Free Range Eggs',
                    'purchase_date': datetime.now().date() - timedelta(days=2),
                    'expiration_date': datetime.now().date() + timedelta(days=11),
                    'price': 5.99
                },
                {
                    'receipt_id': 'REC-2024-001',
                    'product_name': 'Greek Yogurt',
                    'purchase_date': datetime.now().date() - timedelta(days=2),
                    'expiration_date': datetime.now().date() + timedelta(days=6),
                    'price': 3.49
                },
                {
                    'receipt_id': 'REC-2024-001',
                    'product_name': 'Fresh Spinach',
                    'purchase_date': datetime.now().date() - timedelta(days=2),
                    'expiration_date': datetime.now().date() + timedelta(days=5),
                    'price': 2.50
                },
                # Receipt 2 items
                {
                    'receipt_id': 'REC-2024-002',
                    'product_name': 'Chicken Breast',
                    'purchase_date': datetime.now().date() - timedelta(days=1),
                    'expiration_date': datetime.now().date() + timedelta(days=2),
                    'price': 8.99
                },
                {
                    'receipt_id': 'REC-2024-002',
                    'product_name': 'Ground Beef',
                    'purchase_date': datetime.now().date() - timedelta(days=1),
                    'expiration_date': datetime.now().date() + timedelta(days=2),
                    'price': 6.99
                },
                {
                    'receipt_id': 'REC-2024-002',
                    'product_name': 'Salmon Fillet',
                    'purchase_date': datetime.now().date() - timedelta(days=1),
                    'expiration_date': datetime.now().date() + timedelta(days=1),
                    'price': 12.99
                }
            ]
            
            # Add receipts
            receipts_added = 0
            for receipt_data in sample_receipts:
                existing = Receipt.query.filter_by(receipt_id=receipt_data['receipt_id']).first()
                if not existing:
                    receipt = Receipt(**receipt_data)
                    db.session.add(receipt)
                    receipts_added += 1
            
            # Add items
            items_added = 0
            for item_data in sample_items:
                existing = Item.query.filter_by(
                    product_name=item_data['product_name'],
                    receipt_id=item_data['receipt_id']
                ).first()
                if not existing:
                    item = Item(**item_data)
                    db.session.add(item)
                    items_added += 1
            
            # Commit all changes
            db.session.commit()
            
            # Summary
            total_items = Item.query.count()
            total_receipts = Receipt.query.count()
            total_value = db.session.query(db.func.sum(Item.price)).scalar() or 0
            
            print(f"\n=== Sample Data Added ===")
            print(f"Receipts added: {receipts_added}")
            print(f"Items added: {items_added}")
            print(f"Total items in database: {total_items}")
            print(f"Total receipts in database: {total_receipts}")
            print(f"Total value: ${total_value:.2f}")
            
            return True
            
    except Exception as e:
        print(f"✗ Failed to add sample data: {e}")
        return False

def main():
    """Main function"""
    print("Adding sample data to test the frontend...")
    
    success = add_sample_data()
    
    if success:
        print("\n🎉 Sample data added successfully!")
        print("You can now test the frontend with sample data.")
        print("Run: python start.py")
    else:
        print("\n❌ Failed to add sample data.")

if __name__ == '__main__':
    main()

