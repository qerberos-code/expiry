# Deployment Guide for Expiry Tracker

## Deploying to Render.com

### 1. Prerequisites
- GitHub repository (already created: https://github.com/qerberos-code/expiry)
- Render.com account

### 2. Environment Variables
Create a `.env` file with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Application Settings
DEBUG=False
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=production

# Render.com specific settings
PORT=5000
```

### 3. Render.com Setup

#### Step 1: Create PostgreSQL Database
1. Go to Render.com dashboard
2. Click "New +" → "PostgreSQL"
3. Choose "Free" tier (90 days)
4. Name: `expiry-db`
5. Click "Create Database"
6. Copy the connection string (DATABASE_URL)

#### Step 2: Create Web Service
1. Go to Render.com dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `qerberos-code/expiry`
4. Configure:
   - **Name**: `expiry-tracker`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: `Free`

#### Step 3: Set Environment Variables
In your web service settings, add:
- `DATABASE_URL`: (from your PostgreSQL database)
- `SECRET_KEY`: (generate a random secret key)
- `FLASK_ENV`: `production`
- `DEBUG`: `False`

### 4. Database Migration
After deployment, you'll need to initialize the database:

1. Go to your web service's shell/console
2. Run: `python init_db.py`

Or add this to your build command:
```bash
pip install -r requirements.txt && python init_db.py
```

### 5. Custom Domain (Optional)
1. In your web service settings
2. Go to "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

## Local Development Setup

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Install PostgreSQL locally or use Docker
# Create database
createdb expiry_db

# Set environment variables
export DATABASE_URL="postgresql://localhost/expiry_db"
export SECRET_KEY="your-secret-key"
export DEBUG="True"

# Initialize database
python init_db.py
```

### 3. Run Application
```bash
python app.py
```

Visit: http://localhost:5000

## Database Schema

### Items Table
```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    receipt_id VARCHAR(100),
    product_name VARCHAR(200) NOT NULL,
    purchase_date DATE NOT NULL,
    expiration_date DATE,
    price FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Receipts Table
```sql
CREATE TABLE receipts (
    id SERIAL PRIMARY KEY,
    receipt_id VARCHAR(100) UNIQUE NOT NULL,
    store_name VARCHAR(200),
    purchase_date DATE,
    total_amount FLOAT,
    tax_amount FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Features

- ✅ Add/edit/delete items
- ✅ Track expiration dates
- ✅ Dashboard with status overview
- ✅ Items expiring soon alerts
- ✅ Analytics and statistics
- ✅ Responsive design
- ✅ PostgreSQL database
- ✅ Ready for Render.com deployment

## API Endpoints

- `GET /` - Dashboard
- `GET /add_item` - Add item form
- `POST /add_item` - Create new item
- `GET /edit_item/<id>` - Edit item form
- `POST /edit_item/<id>` - Update item
- `POST /delete_item/<id>` - Delete item
- `GET /expiring_soon` - Items expiring within 7 days
- `GET /analytics` - Statistics and analytics
- `GET /api/items` - JSON API for all items

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL format
   - Ensure PostgreSQL is running
   - Verify credentials

2. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Template Not Found**
   - Ensure templates/ directory exists
   - Check file permissions

4. **Static Files Not Loading**
   - Check static/ directory structure
   - Verify CSS/JS file paths

### Render.com Specific

1. **Build Failures**
   - Check build logs
   - Ensure all dependencies in requirements.txt
   - Verify Python version compatibility

2. **Runtime Errors**
   - Check application logs
   - Verify environment variables
   - Test database connection

3. **Database Issues**
   - Ensure PostgreSQL service is running
   - Check connection string format
   - Run database migrations

## Support

For issues or questions:
1. Check the logs in Render.com dashboard
2. Review this deployment guide
3. Test locally first
4. Check GitHub repository for updates
