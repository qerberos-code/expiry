#!/usr/bin/env python3
"""
Simple Flask app for Expiry Tracker - minimal startup
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_migrate import Migrate
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64
import io
from PIL import Image
import json
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration with fallback
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Use SQLite for development/testing
    database_url = 'sqlite:///expiry.db'
    print("Using SQLite database for local development")

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
        items = Item.query.order_by(Item.expiration_date.asc().nulls_last()).all()
        print(f"Found {len(items)} items in database")
        for item in items:
            print(f"- {item.product_name}: {item.expiration_date}")
        print(f"Rendering template with {len(items)} items")
        return render_template('mobile_index_fixed.html', items=items)
    except Exception as e:
        print(f"Database error: {e}")
        return render_template('mobile_index_fixed.html', items=[])

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        if DATABASE_AVAILABLE:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
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
        'database_url': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set'),
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/debug')
def debug():
    """Debug endpoint to test database queries"""
    if not DATABASE_AVAILABLE:
        return jsonify({'error': 'Database not available'})
    
    try:
        items = Item.query.all()
        items_data = []
        for item in items:
            items_data.append({
                'id': item.id,
                'product_name': item.product_name,
                'expiration_date': item.expiration_date.isoformat() if item.expiration_date else None,
                'status': item.status,
                'price': item.price
            })
        
        return jsonify({
            'total_items': len(items),
            'items': items_data,
            'database_url': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/test_template')
def test_template():
    """Test template rendering"""
    if not DATABASE_AVAILABLE:
        return render_template('test.html', items=[])
    
    try:
        items = Item.query.all()
        print(f"Passing {len(items)} items to template")
        return render_template('test.html', items=items)
    except Exception as e:
        print(f"Template error: {e}")
        return render_template('test.html', items=[])

@app.route('/expiring_soon')
def expiring_soon():
    """Show items expiring soon"""
    if not DATABASE_AVAILABLE:
        return render_template('mobile_items_list.html', items=[])
    
    try:
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        items = Item.query.filter(
            Item.expiration_date >= today,
            Item.expiration_date <= next_week
        ).order_by(Item.expiration_date.asc()).all()
        return render_template('mobile_items_list.html', items=items)
    except Exception as e:
        print(f"Database error: {e}")
        return render_template('mobile_items_list.html', items=[])

@app.route('/analytics')
def analytics():
    """Show analytics"""
    if not DATABASE_AVAILABLE:
        return jsonify({'error': 'Database not available'})
    
    try:
        total_items = Item.query.count()
        today = datetime.now().date()
        expired_count = Item.query.filter(Item.expiration_date < today).count()
        expiring_soon_count = Item.query.filter(
            Item.expiration_date >= today,
            Item.expiration_date <= today + timedelta(days=3)
        ).count()
        total_value = db.session.query(db.func.sum(Item.price)).scalar() or 0
        
        return jsonify({
            'total_items': total_items,
            'expired_count': expired_count,
            'expiring_soon_count': expiring_soon_count,
            'total_value': total_value
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/camera')
def camera_capture():
    """Camera capture page for receipt scanning"""
    return render_template('camera_capture.html')

@app.route('/process_receipt', methods=['POST'])
def process_receipt():
    """Process receipt image from camera"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Extract base64 image data
        image_data = data['image']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode and process image
        image_bytes = base64.b64decode(image_data)
        
        # Generate unique filename
        image_id = str(uuid.uuid4())
        filename = f"receipt_{image_id}.jpg"
        
        # Ensure receipts directory exists
        receipts_dir = os.path.join(app.root_path, 'receipts')
        os.makedirs(receipts_dir, exist_ok=True)
        
        # Save image to disk
        image_path = os.path.join(receipts_dir, filename)
        
        # Process and save image with PIL
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Save as JPEG
            img.save(image_path, 'JPEG', quality=85, optimize=True)
        
        print(f"Image saved to: {image_path}")
        
        # For now, return mock data - in production you'd use OCR
        mock_receipt_data = {
            'is_receipt': True,
            'vendor': 'Safeway',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total': '$45.67',
            'image_path': f"receipts/{filename}",
            'image_id': image_id,
            'items': [
                {'name': 'Organic Milk', 'price': 4.99, 'expiration_days': 7},
                {'name': 'Whole Wheat Bread', 'price': 2.49, 'expiration_days': 5},
                {'name': 'Free Range Eggs', 'price': 5.99, 'expiration_days': 14},
                {'name': 'Greek Yogurt', 'price': 3.99, 'expiration_days': 10},
                {'name': 'Fresh Spinach', 'price': 2.99, 'expiration_days': 3}
            ]
        }
        
        return jsonify(mock_receipt_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/receipts/<filename>')
def serve_receipt_image(filename):
    """Serve uploaded receipt images"""
    try:
        receipts_dir = os.path.join(app.root_path, 'receipts')
        image_path = os.path.join(receipts_dir, filename)
        
        if os.path.exists(image_path):
            from flask import send_file
            return send_file(image_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_receipt_items', methods=['POST'])
def save_receipt_items():
    """Save extracted receipt items to database"""
    if not DATABASE_AVAILABLE:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        saved_items = []
        for item_data in items:
            # Calculate expiration date
            expiration_date = datetime.now().date() + timedelta(days=item_data.get('expiration_days', 7))
            
            # Create new item
            item = Item(
                receipt_id=f"REC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                product_name=item_data['name'],
                purchase_date=datetime.now().date(),
                expiration_date=expiration_date,
                price=item_data['price']
            )
            
            db.session.add(item)
            saved_items.append({
                'name': item.product_name,
                'expiration_date': expiration_date.strftime('%Y-%m-%d'),
                'price': item.price
            })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'saved_items': saved_items,
            'message': f'Successfully saved {len(saved_items)} items'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
