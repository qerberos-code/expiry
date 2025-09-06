#!/usr/bin/env python3
"""
Simple Flask app for Expiry Tracker - minimal startup
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_migrate import Migrate
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration with fallback
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Use SQLite for development/testing
    database_url = 'sqlite:///expiry.db'
    print("Warning: DATABASE_URL not set, using SQLite fallback")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Try to import models, but don't fail if database is not available
try:
    from models import db, Item, Receipt
    db.init_app(app)
    migrate = Migrate(app, db)
    DATABASE_AVAILABLE = True
    print("Database models loaded successfully")
except Exception as e:
    print(f"Database models not available: {e}")
    DATABASE_AVAILABLE = False

@app.route('/')
def index():
    """Simple home page"""
    if not DATABASE_AVAILABLE:
        return render_template('mobile_index.html', items=[])
    
    try:
        items = Item.query.order_by(Item.expirationDate.asc().nulls_last()).all()
        return render_template('mobile_index.html', items=items)
    except Exception as e:
        print(f"Database error: {e}")
        return render_template('mobile_index.html', items=[])

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        if DATABASE_AVAILABLE:
            db.session.execute('SELECT 1')
            db_status = 'connected'
        else:
            db_status = 'not_available'
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat(),
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    """Add item form"""
    if request.method == 'POST' and DATABASE_AVAILABLE:
        try:
            from models import Item
            
            product_name = request.form['productName']
            purchase_date = datetime.strptime(request.form['purchaseDate'], '%Y-%m-%d').date()
            expiration_date = None
            if request.form.get('expirationDate'):
                expiration_date = datetime.strptime(request.form['expirationDate'], '%Y-%m-%d').date()
            price = float(request.form['price'])
            receipt_id = request.form.get('receiptId', '') or None
            
            item = Item(
                receipt_id=receipt_id,
                product_name=product_name,
                purchase_date=purchase_date,
                expiration_date=expiration_date,
                price=price
            )
            
            db.session.add(item)
            db.session.commit()
            
            flash(f'Item "{product_name}" added successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {str(e)}', 'error')
    
    return render_template('mobile_add_item.html')

@app.route('/test')
def test():
    """Simple test endpoint"""
    return jsonify({
        'message': 'Expiry Tracker is running!',
        'timestamp': datetime.now().isoformat(),
        'database_available': DATABASE_AVAILABLE,
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    if DATABASE_AVAILABLE:
        db.session.rollback()
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please try again later',
        'timestamp': datetime.now().isoformat()
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Page not found',
        'message': 'The requested page does not exist',
        'timestamp': datetime.now().isoformat()
    }), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"Starting Expiry Tracker...")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Database available: {DATABASE_AVAILABLE}")
    print(f"Database URL: {database_url[:20]}..." if database_url else "No database URL")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
