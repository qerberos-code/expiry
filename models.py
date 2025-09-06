from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()

class Item(db.Model):
    """Item model matching the specified document structure"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.String(100), nullable=True, index=True)
    product_name = db.Column(db.String(200), nullable=False, index=True)
    purchase_date = db.Column(db.Date, nullable=False, index=True)
    expiration_date = db.Column(db.Date, nullable=True, index=True)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Item {self.product_name}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'receiptId': self.receipt_id,
            'productName': self.product_name,
            'purchaseDate': self.purchase_date.isoformat() if self.purchase_date else None,
            'expirationDate': self.expiration_date.isoformat() if self.expiration_date else None,
            'price': self.price,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def days_until_expiration(self):
        """Calculate days until expiration"""
        if not self.expiration_date:
            return None
        
        today = datetime.now().date()
        return (self.expiration_date - today).days
    
    @property
    def status(self):
        """Get expiration status"""
        if not self.expiration_date:
            return 'no_expiration'
        
        days = self.days_until_expiration
        if days < 0:
            return 'expired'
        elif days <= 3:
            return 'expiring_soon'
        elif days <= 7:
            return 'expiring_this_week'
        else:
            return 'fresh'

class Receipt(db.Model):
    """Receipt model for storing receipt information"""
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    store_name = db.Column(db.String(200), nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    total_amount = db.Column(db.Float, nullable=True)
    tax_amount = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with items
    items = db.relationship('Item', backref='receipt', lazy=True, foreign_keys='Item.receipt_id', primaryjoin='Receipt.receipt_id == Item.receipt_id')
    
    def __repr__(self):
        return f'<Receipt {self.receipt_id}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'receiptId': self.receipt_id,
            'storeName': self.store_name,
            'purchaseDate': self.purchase_date.isoformat() if self.purchase_date else None,
            'totalAmount': self.total_amount,
            'taxAmount': self.tax_amount,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }
