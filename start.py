#!/usr/bin/env python3
"""
Startup script for Expiry Tracker
Handles database initialization and app startup
"""

import os
import sys
from app import app, db
from models import Item, Receipt
from datetime import datetime, timedelta

def init_database():
    """Initialize database with tables and sample data"""
    try:
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if we already have data
        if Item.query.count() > 0:
            print("Database already contains data. Skipping sample data insertion.")
            return True
        
        # Add sample data
        print("Adding sample data...")
        
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
            )
        ]
        
        for item in sample_items:
            db.session.add(item)
        
        db.session.commit()
        print("✓ Sample data added successfully")
        return True
        
    except Exception as e:
        print(f"✗ Database initialization failed: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Main startup function"""
    print("Starting Expiry Tracker...")
    
    # Check environment variables
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Warning: DATABASE_URL not set!")
        print("The app will use a fallback database URL")
    else:
        print(f"Database URL configured: {database_url[:20]}...")
    
    # Initialize database
    if not init_database():
        print("Failed to initialize database. Starting app anyway...")
    
    # Start the app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"Starting Flask app on port {port} (debug={debug})")
    app.run(debug=debug, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
