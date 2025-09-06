# extract_grocery_items.py
"""
Grocery Receipt Reader
----------------------
Reads a grocery receipt image and extracts:
- Items (abbreviations → inferred full names)
- Purchase date (falls back to user input if not found)
- Estimated shelf life & expiration dates
- Final total cost

Requires:
    pip install google-generativeai
"""

import os
import imghdr
import re
import google.generativeai as genai

try:
    from google.colab import files
except ImportError:
    files = None

# -----------------------------
# Configure API key
# -----------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY. Set it as an environment variable.")
genai.configure(api_key=API_KEY)

# -----------------------------
# Upload receipt image
# -----------------------------
if files:
    uploaded = files.upload()
    image_path = next(iter(uploaded.keys()))
else:
    raise RuntimeError("This script is designed to run in Google Colab for file upload.")

mime = imghdr.what(image_path)
mime_type = f"image/{mime}" if mime in ("jpeg", "png", "webp", "heic", "heif") else "image/jpeg"

askDate = input("What is the date of purchase? (MM/DD/YYYY) ")

# -----------------------------
# Model setup
# -----------------------------
model = genai.GenerativeModel("gemini-1.5-flash")

PROMPT = f"""
System / Instruction prompt
You are a grocery receipt reader. You will be given one image of a grocery receipt. Your tasks are:

1. Extract the item line names exactly as abbreviated on the receipt.
2. Capture the final total cost.
3. Using the extracted abbreviated item names, infer what their full names might be as common grocery items.
5. Estimate the shelf life of each item:
   - If the item is nonperishable (e.g., canned goods, dry pasta, rice), assume unlimited shelf life.
   - If the item is perishable (e.g., fresh produce, meat, dairy), estimate a reasonable number of days until it expires.
6. Add the shelf life to the purchase date to determine the expiration date for each item.

Important:
- If no purchase date is detected in the receipt, substitute with the provided fallback date: {askDate}.
- Make sure every item line includes a purchase date (never leave it blank).
"""

# -----------------------------
# Run model
# -----------------------------
with open(image_path, "rb") as f:
    image_bytes = f.read()

resp = model.generate_content(
    [
        {"mime_type": mime_type, "data": image_bytes},
        PROMPT,
    ]
)

# -----------------------------
# Parse + display
# -----------------------------
text = (resp.text or "").strip()
lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

# Replace "NOT FOUND" with fallback date
updated_lines = []
date_pattern = re.compile(r"Purchase Date:\s*NOT FOUND", re.IGNORECASE)
for ln in lines:
    if date_pattern.search(ln):
        ln = date_pattern.sub(f"Purchase Date: {askDate}", ln)
    updated_lines.append(ln)

food_items = [ln[1:].strip() if ln.startswith("*") else ln for ln in updated_lines]

print("List of Food Items:")
for item in food_items:
    print("-", item)
