from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['flask_nosql_db']
collection = db['data_collection']

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder

@app.route('/store', methods=['POST'])
def store_data():
    """
    Endpoint to store JSON data in the NoSQL database
    Expects JSON payload in the request body
    """
    try:
        # TODO: Add receipt items through this.

        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Add timestamp to the data
        data['timestamp'] = datetime.utcnow()
        
        # Insert data into MongoDB
        result = collection.insert_one(data)
        
        return jsonify({
            'message': 'Data stored successfully',
            'id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data', methods=['GET'])
def get_all_data():
    """
    Endpoint to retrieve all data from the NoSQL database
    Returns all receipts in the collection
    """
    try:
        # Retrieve all receipts from the collection
        receipts = list(collection.find())
        
        # Convert ObjectId to string for JSON serialization
        for doc in receipts:
            doc['_id'] = str(doc['_id'])
            if 'timestamp' in doc:
                doc['timestamp'] = doc['timestamp'].isoformat()
        
        return jsonify({
            'count': len(receipts),
            'data': receipts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    """
    Basic health check endpoint
    """
    return jsonify({
        'message': 'Flask NoSQL API is running',
        'endpoints': {
            'POST /store': 'Store JSON data',
            'GET /data': 'Retrieve all data'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
