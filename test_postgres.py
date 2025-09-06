#!/usr/bin/env python3
"""
Test PostgreSQL database connection and functionality
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_postgres():
    """Test PostgreSQL database"""
    
    print("=== PostgreSQL Database Test ===")
    
    # Check environment
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"Database URL: {database_url[:30]}...")
    else:
        print("No DATABASE_URL found, will use SQLite fallback")
    
    try:
        from app import app, db
        from models import Item, Receipt
        from datetime import datetime, timedelta
        
        print("✓ Successfully imported models")
        
        with app.app_context():
            print("✓ App context created")
            
            # Test database connection
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                print("✓ Database connection successful")
            except Exception as e:
                print(f"✗ Database connection failed: {e}")
                return False
            
            # Test table creation
            try:
                db.create_all()
                print("✓ Tables created/verified")
            except Exception as e:
                print(f"✗ Table creation failed: {e}")
                return False
            
            # Test basic queries
            try:
                item_count = Item.query.count()
                receipt_count = Receipt.query.count()
                print(f"✓ Basic queries work - Items: {item_count}, Receipts: {receipt_count}")
            except Exception as e:
                print(f"✗ Basic queries failed: {e}")
                return False
            
            # Test adding a sample item
            try:
                test_item = Item(
                    receipt_id="TEST-001",
                    product_name="Test Product",
                    purchase_date=datetime.now().date(),
                    expiration_date=datetime.now().date() + timedelta(days=7),
                    price=9.99
                )
                
                # Check if test item already exists
                existing = Item.query.filter_by(
                    product_name="Test Product",
                    receipt_id="TEST-001"
                ).first()
                
                if not existing:
                    db.session.add(test_item)
                    db.session.commit()
                    print("✓ Successfully added test item")
                    
                    # Clean up test item
                    db.session.delete(test_item)
                    db.session.commit()
                    print("✓ Successfully removed test item")
                else:
                    print("✓ Test item already exists (skipping add/remove test)")
                    
            except Exception as e:
                print(f"✗ Add/remove test failed: {e}")
                return False
            
            print("\n🎉 PostgreSQL database is working correctly!")
            return True
            
    except Exception as e:
        print(f"✗ PostgreSQL test failed: {e}")
        return False

if __name__ == '__main__':
    test_postgres()
