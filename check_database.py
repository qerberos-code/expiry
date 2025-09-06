#!/usr/bin/env python3
"""
Check what's in the PostgreSQL database
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database():
    """Check PostgreSQL database contents"""
    
    print("=== PostgreSQL Database Contents ===")
    
    try:
        from app import app, db
        from models import Item, Receipt
        
        with app.app_context():
            # Check if tables exist
            print("✓ Connected to PostgreSQL database")
            
            # Count items
            total_items = Item.query.count()
            print(f"\n--- Items Table ---")
            print(f"Total items: {total_items}")
            
            if total_items > 0:
                # Show all items
                items = Item.query.all()
                print(f"\nAll items:")
                for i, item in enumerate(items, 1):
                    print(f"  {i}. {item.product_name}")
                    print(f"     Receipt ID: {item.receipt_id}")
                    print(f"     Purchase Date: {item.purchase_date}")
                    print(f"     Expiration Date: {item.expiration_date}")
                    print(f"     Price: ${item.price:.2f}")
                    print(f"     Status: {item.status}")
                    print(f"     Days until expiration: {item.days_until_expiration}")
                    print()
            else:
                print("  No items found")
            
            # Count receipts
            total_receipts = Receipt.query.count()
            print(f"\n--- Receipts Table ---")
            print(f"Total receipts: {total_receipts}")
            
            if total_receipts > 0:
                # Show all receipts
                receipts = Receipt.query.all()
                print(f"\nAll receipts:")
                for i, receipt in enumerate(receipts, 1):
                    print(f"  {i}. Receipt ID: {receipt.receipt_id}")
                    print(f"     Store: {receipt.store_name}")
                    print(f"     Purchase Date: {receipt.purchase_date}")
                    print(f"     Total Amount: ${receipt.total_amount:.2f}")
                    print(f"     Tax Amount: ${receipt.tax_amount:.2f}")
                    print(f"     Items Count: {len(receipt.items)}")
                    print()
            else:
                print("  No receipts found")
            
            # Summary statistics
            if total_items > 0:
                total_value = db.session.query(db.func.sum(Item.price)).scalar() or 0
                expired_count = Item.query.filter(Item.expiration_date < datetime.now().date()).count()
                expiring_soon_count = Item.query.filter(
                    Item.expiration_date >= datetime.now().date(),
                    Item.expiration_date <= datetime.now().date() + timedelta(days=3)
                ).count()
                
                print(f"\n--- Summary Statistics ---")
                print(f"Total value: ${total_value:.2f}")
                print(f"Expired items: {expired_count}")
                print(f"Expiring soon (≤3 days): {expiring_soon_count}")
            
            return True
            
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False

if __name__ == '__main__':
    from datetime import datetime, timedelta
    check_database()

