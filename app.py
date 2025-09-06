from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models import db, Item, Receipt

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# PostgreSQL configuration
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Fallback for development
    database_url = 'postgresql://localhost/expiry_db'
    print("Warning: DATABASE_URL not set, using fallback")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    """Main dashboard showing all items with expiration tracking"""
    items = Item.query.order_by(Item.expirationDate.asc().nulls_last()).all()
    return render_template('mobile_index.html', items=items)

@app.route('/desktop')
def desktop_index():
    """Desktop version of the dashboard"""
    items = Item.query.order_by(Item.expirationDate.asc().nulls_last()).all()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    """Add a new item to the database"""
    if request.method == 'POST':
        try:
            # Parse form data
            product_name = request.form['productName']
            purchase_date = datetime.strptime(request.form['purchaseDate'], '%Y-%m-%d').date()
            expiration_date = None
            if request.form.get('expirationDate'):
                expiration_date = datetime.strptime(request.form['expirationDate'], '%Y-%m-%d').date()
            price = float(request.form['price'])
            receipt_id = request.form.get('receiptId', '') or None
            
            # Create item
            item = Item(
                receipt_id=receipt_id,
                product_name=product_name,
                purchase_date=purchase_date,
                expiration_date=expiration_date,
                price=price
            )
            
            # Add to database
            db.session.add(item)
            db.session.commit()
            
            flash(f'Item "{product_name}" added successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {str(e)}', 'error')
            return render_template('mobile_add_item.html')
    
    return render_template('mobile_add_item.html')

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit an existing item"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            # Parse form data
            item.product_name = request.form['productName']
            item.purchase_date = datetime.strptime(request.form['purchaseDate'], '%Y-%m-%d').date()
            item.expiration_date = None
            if request.form.get('expirationDate'):
                item.expiration_date = datetime.strptime(request.form['expirationDate'], '%Y-%m-%d').date()
            item.price = float(request.form['price'])
            item.receipt_id = request.form.get('receiptId', '') or None
            
            # Update in database
            db.session.commit()
            
            flash(f'Item "{item.product_name}" updated successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating item: {str(e)}', 'error')
            return redirect(url_for('edit_item', item_id=item_id))
    
    return render_template('edit_item.html', item=item)

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    """Delete an item from the database"""
    try:
        item = Item.query.get_or_404(item_id)
        product_name = item.product_name
        db.session.delete(item)
        db.session.commit()
        flash(f'Item "{product_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting item: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/items')
def api_items():
    """API endpoint to get all items as JSON"""
    items = Item.query.order_by(Item.expirationDate.asc().nulls_last()).all()
    return jsonify([item.to_dict() for item in items])

@app.route('/expiring_soon')
def expiring_soon():
    """Show items expiring within the next 7 days"""
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    items = Item.query.filter(
        Item.expiration_date >= today,
        Item.expiration_date <= next_week
    ).order_by(Item.expiration_date.asc()).all()
    
    return render_template('mobile_items_list.html', items=items)

@app.route('/items_list')
def items_list():
    """Show all items organized by category"""
    items = Item.query.order_by(Item.expirationDate.asc().nulls_last()).all()
    return render_template('mobile_items_list.html', items=items)

@app.route('/receipt_details')
def receipt_details():
    """Show receipt details with items"""
    items = Item.query.order_by(Item.purchase_date.desc()).all()
    return render_template('mobile_receipt_details.html', items=items)

@app.route('/analytics')
def analytics():
    """Show analytics and statistics"""
    total_items = Item.query.count()
    
    # Items by status
    today = datetime.now().date()
    expired_count = Item.query.filter(Item.expiration_date < today).count()
    
    expiring_soon_count = Item.query.filter(
        Item.expiration_date >= today,
        Item.expiration_date <= today + timedelta(days=3)
    ).count()
    
    # Total value
    total_value = db.session.query(db.func.sum(Item.price)).scalar() or 0
    
    analytics_data = {
        'total_items': total_items,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon_count,
        'total_value': total_value
    }
    
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500,
                         error_message="Internal server error. Please try again later."), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html',
                         error_code=404,
                         error_message="Page not found."), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
