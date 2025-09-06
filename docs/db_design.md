# Database Design: Expiry Tracker

This document outlines the design of the MongoDB database (`expiry`) for the Expiry Tracker application.

## Collections

The database consists of two main collections: `receipts` and `items`.

---

### `receipts` Collection

Stores one document for each grocery receipt.

**Schema and Validation:**

| Field         | Data Type | Required | Description                               |
|---------------|-----------|----------|-------------------------------------------|
| `_id`         | ObjectId  | Yes      | Unique identifier for the receipt document. |
| `storeName`   | String    | Yes      | The name of the store (e.g., "Safeway").  |
| `purchaseDate`| Date      | Yes      | The date and time of the purchase.        |
| `totalAmount` | Number    | Yes      | The total amount of the receipt.          |

---

### `items` Collection

Stores one document for each item listed on a receipt.

**Schema and Validation:**

| Field            | Data Type | Required | Description                                                  |
|------------------|-----------|----------|--------------------------------------------------------------|
| `_id`            | ObjectId  | Yes      | Unique identifier for the item document.                     |
| `receiptId`      | ObjectId  | Yes      | References the `_id` of the parent document in `receipts`.   |
| `productName`    | String    | Yes      | The name of the product (e.g., "Organic Milk").              |
| `price`          | Number    | Yes      | The price of the individual item.                            |
| `purchaseDate`   | Date      | No       | The date of purchase (can be inherited from the receipt).    |
| `expirationDate` | Date      | No       | The predicted or actual expiration date of the item.         |
| `category`       | String    | No       | The product category (e.g., "Dairy", "Produce").             |
