#!/usr/bin/env python3
"""
Database initialization script for Expiry Tracker
Creates tables and adds sample data
"""

from app import app, db
from models import Item, Receipt
from datetime import datetime, timedelta
import os

def init_database():
    """Initialize the database with tables and sample data"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if we already have data
        if Item.query.count() > 0:
            print("Database already contains data. Skipping sample data insertion.")
            return
        
        # Add sample data
        print("Adding sample data...")
        
        # Sample items
        sample_items = [
            Item(
                receipt_id="REC-2024-001",
                product_name="Organic Milk",
                purchase_date=datetime.now().date() - timedelta(days=2),
                expiration_date=datetime.now().date() + timedelta(days=5),
                price=4.99
            ),
            Item(
                receipt_id="REC-2024-001",
                product_name="Whole Wheat Bread",
                purchase_date=datetime.now().date() - timedelta(days=1),
                expiration_date=datetime.now().date() + timedelta(days=4),
                price=2.49
            ),
            Item(
                receipt_id="REC-2024-002",
                product_name="Free Range Eggs",
                purchase_date=datetime.now().date() - timedelta(days=3),
                expiration_date=datetime.now().date() + timedelta(days=11),
                price=5.99
            ),
            Item(
                receipt_id="REC-2024-002",
                product_name="Greek Yogurt",
                purchase_date=datetime.now().date() - timedelta(days=1),
                expiration_date=datetime.now().date() + timedelta(days=6),
                price=3.49
            ),
            Item(
                receipt_id="REC-2024-003",
                product_name="Fresh Spinach",
                purchase_date=datetime.now().date() - timedelta(days=2),
                expiration_date=datetime.now().date() + timedelta(days=5),
                price=2.50
            ),
            Item(
                receipt_id="REC-2024-003",
                product_name="Organic Baby Lettuce",
                purchase_date=datetime.now().date() - timedelta(days=2),
                expiration_date=datetime.now().date() + timedelta(days=5),
                price=2.50
            ),
            Item(
                receipt_id="REC-2024-004",
                product_name="Orange Bell Pepper",
                purchase_date=datetime.now().date() - timedelta(days=1),
                expiration_date=datetime.now().date() + timedelta(days=6),
                price=1.99
            ),
            Item(
                receipt_id="REC-2024-004",
                product_name="Navel Oranges",
                purchase_date=datetime.now().date() - timedelta(days=1),
                expiration_date=datetime.now().date() + timedelta(days=12),
                price=2.48
            ),
            Item(
                receipt_id="REC-2024-005",
                product_name="Chicken Breast",
                purchase_date=datetime.now().date() - timedelta(days=1),
                expiration_date=datetime.now().date() + timedelta(days=2),
                price=8.99
            ),
            Item(
                receipt_id="REC-2024-005",
                product_name="Ground Beef",
                purchase_date=datetime.now().date() - timedelta(days=1),
                expiration_date=datetime.now().date() + timedelta(days=2),
                price=6.99
            )
        ]
        
        # Add items to database
        for item in sample_items:
            db.session.add(item)
        
        # Add sample receipts
        sample_receipts = [
            Receipt(
                receipt_id="REC-2024-001",
                store_name="Safeway",
                purchase_date=datetime.now().date() - timedelta(days=2),
                total_amount=7.48,
                tax_amount=0.58
            ),
            Receipt(
                receipt_id="REC-2024-002",
                store_name="Whole Foods",
                purchase_date=datetime.now().date() - timedelta(days=3),
                total_amount=9.48,
                tax_amount=0.75
            ),
            Receipt(
                receipt_id="REC-2024-003",
                store_name="Trader Joe's",
                purchase_date=datetime.now().date() - timedelta(days=2),
                total_amount=5.00,
                tax_amount=0.40
            ),
            Receipt(
                receipt_id="REC-2024-004",
                store_name="Safeway",
                purchase_date=datetime.now().date() - timedelta(days=1),
                total_amount=4.47,
                tax_amount=0.36
            ),
            Receipt(
                receipt_id="REC-2024-005",
                store_name="Costco",
                purchase_date=datetime.now().date() - timedelta(days=1),
                total_amount=15.98,
                tax_amount=1.28
            )
        ]
        
        # Add receipts to database
        for receipt in sample_receipts:
            db.session.add(receipt)
        
        # Commit all changes
        db.session.commit()
        print("✓ Sample data added successfully")
        
        # Print summary
        total_items = Item.query.count()
        total_receipts = Receipt.query.count()
        total_value = db.session.query(db.func.sum(Item.price)).scalar()
        
        print(f"\nDatabase initialized successfully!")
        print(f"Total items: {total_items}")
        print(f"Total receipts: {total_receipts}")
        print(f"Total value: ${total_value:.2f}")

if __name__ == '__main__':
    init_database()
