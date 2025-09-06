from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, ValidationError
from typing import List, Optional

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://2.tcp.ngrok.io:10482')
db = client['flask_nosql_db']
receipts_collection = db['receipts']
items_collection = db['items']


# --- Pydantic Models for Validation ---
class ItemModel(BaseModel):
    productName: str
    price: float
    # These fields are optional in the input JSON
    expirationDate: Optional[datetime] = None


class ReceiptModel(BaseModel):
    storeName: str
    purchaseDate: datetime
    totalAmount: float
    items: List[ItemModel] = []


@app.route("/receipts", methods=["POST"])
def create_receipt():
    """
    Endpoint to store a new receipt with its items.
    The incoming JSON is validated against the Pydantic models.
    """
    try:
        # 1. Validate incoming JSON against our Pydantic model
        receipt_data = ReceiptModel(**request.get_json())

    except ValidationError as e:
        # If validation fails, return a 400 error with details
        return (
            jsonify({"error": "Invalid data provided", "details": e.errors()}),
            400,
        )

    try:
        # 2. Insert the valid receipt data
        receipt_to_insert = {
            "storeName": receipt_data.storeName,
            "purchaseDate": receipt_data.purchaseDate,
            "totalAmount": receipt_data.totalAmount,
        }
        result = receipts_collection.insert_one(receipt_to_insert)
        receipt_id = result.inserted_id

        # 3. Prepare and insert the associated items
        items_to_insert = []
        if receipt_data.items:
            for item in receipt_data.items:
                item_doc = item.dict()
                item_doc["receiptId"] = receipt_id
                # Always use the receipt's purchase date for the item
                item_doc["purchaseDate"] = receipt_data.purchaseDate
                items_to_insert.append(item_doc)

            if items_to_insert:
                items_collection.insert_many(items_to_insert)

        return (
            jsonify(
                {
                    "message": "Receipt and items stored successfully",
                    "receiptId": str(receipt_id),
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health_check():
    """
    Basic health check endpoint
    """
    return jsonify(
        {
            "message": "Expiry Tracker API is running",
            "endpoints": {
                "POST /receipts": "Store a new receipt and its items"
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
