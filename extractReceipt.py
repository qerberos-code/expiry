# app.py
import os
import imghdr
import re
import json
from typing import List, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

import google.generativeai as genai

# -----------------------------
# Config
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable.")
genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"

app = FastAPI(title="Receipt Reader API")

# -----------------------------
# Prompt (same as your spec)
# -----------------------------
PROMPT = """
System / Instruction prompt
You are a grocery receipt reader. You will be given one image of a grocery receipt. Your tasks are:


1. Extract the item line names exactly as abbreviated on the receipt.
2. Capture the final total cost.
3. Using the extracted abbreviated item names, infer what their full names might be as common grocery items.
5. Estimate the shelf life of each item:
   - If the item is nonperishable (e.g., canned goods, dry pasta, rice), assume unlimited shelf life.
   - If the item is perishable (e.g., fresh produce, meat, dairy), estimate a reasonable number of days until it expires.
6. Add the shelf life to the purchase date to determine the expiration date for each item.


What to extract
- Item names only — keep the original abbreviations exactly as printed (e.g., IMPOSS BURG, BNLS CHICK BREAST).
- Total cost — capture the final amount due: prefer the line labeled TOTAL, AMOUNT DUE, or BALANCE DUE. If multiple totals exist (e.g., subtotal, tax, total), pick the final amount after tax. Ignore “CHANGE”, “CASH BACK”, payment tenders, or running balances.
- Create a list of the original abbreviations exactly as printed (List A).
- Purchase date from the receipt.
- Expiration date for each item based on estimated shelf life.


What to ignore
- Store name/address, cashier, terminal, barcodes.
- Subtotals, tax lines, discounts/coupons/rebates, voids, refunds, payment lines, loyalty info.
- Any line that is not a purchasable item’s name.


OCR hygiene
- Normalize whitespace (single spaces), preserve ASCII punctuation as-is, and strip leading/trailing spaces.
- Keep original capitalization in the abbreviated list (do not title-case or expand abbreviations).
- If an item name is split across two wrapped lines, merge into one name exactly as it would read (no added punctuation).
- If no valid total is found, output NOT FOUND.
- Duplicate handling: If the same item name appears multiple times, repeat it for each occurrence.


Output format


Return a structured list for each item including:


- Full Name
- Estimated Shelf Life
- Expiration Date


Format:


*<Full item name> | Purchase Date: <MM/DD/YYYY> | Shelf Life: <X days or unlimited> | Expiration Date: <MM/DD/YYYY or unlimited>


Rules
- Each item line begins with * immediately followed by the information (no extra spaces before/after).
- The last line must be *TOTAL: ... (e.g., *TOTAL: $53.27).
- Keep the order of items the same as on the receipt.


Few-shot example


Example 1 (input image contains lines like):
KROGER #141
BNLS CHICK BREAST   2.15 lb @ 4.99/lb     10.73
IMPOSS BURG         2 @ 5.99               11.98
ROMA TOMATO         0.80 lb @ 1.29/lb       1.03
SUBTOTAL                                    23.74
TAX                                         1.78
TOTAL                                       $25.52
VISA TEND                                   $25.52
DATE: 03/15/2025


Output:


*Boneless Chicken Breast | Purchase Date: 03/15/2025 | Shelf Life: 7 days | Expiration Date: 03/22/2025
*Impossible Burger | Purchase Date: 03/15/2025 | Shelf Life: 30 days | Expiration Date: 04/14/2025
*Roma Tomato | Purchase Date: 03/15/2025 | Shelf Life: 5 days | Expiration Date: 03/20/2025
*TOTAL: $25.52

"""

# -----------------------------
# Helper: parse model output
# -----------------------------
def parse_output(raw_text: str) -> Dict[str, Any]:
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    star_lines = [ln for ln in lines if ln.startswith("*")]

    item_re = re.compile(
        r'^\*\s*(?P<full_name>.*?)\s*\|\s*Purchase Date:\s*(?P<purchase_date>(?:\d{2}/\d{2}/\d{4}|NOT FOUND))\s*\|\s*Shelf Life:\s*(?P<shelf_life>[^|]+)\s*\|\s*Expiration Date:\s*(?P<expiration_date>.+?)\s*$',
        re.IGNORECASE,
    )
    total_re = re.compile(r'^\*\s*TOTAL:\s*(?P<amount>\$?\s*\d+(?:\.\d{2})?)\s*$', re.IGNORECASE)

    items, total_amount = [], None
    for ln in star_lines:
        m_item = item_re.match(ln)
        if m_item:
            items.append(
                {
                    "full_name": m_item.group("full_name").strip(),
                    "purchase_date": m_item.group("purchase_date").strip(),
                    "shelf_life": m_item.group("shelf_life").strip(),
                    "expiration_date": m_item.group("expiration_date").strip(),
                    "raw": ln,
                }
            )
            continue
        m_total = total_re.match(ln)
        if m_total:
            total_amount = m_total.group("amount").replace(" ", "")

    return {
        "raw_output": star_lines,
        "items": [
            {
                "full_name": i["full_name"],
                "purchase_date": i["purchase_date"],
                "shelf_life": i["shelf_life"],
                "expiration_date": i["expiration_date"],
            }
            for i in items
        ],
        "total": total_amount if total_amount else "NOT FOUND",
    }

# -----------------------------
# API endpoint
# -----------------------------
@app.post("/process-receipt")
async def process_receipt(file: UploadFile = File(...)):
    # validate mime
    mime = imghdr.what(file.file)
    mime_type = f"image/{mime}" if mime in ("jpeg","png","webp","heic","heif") else "image/jpeg"
    image_bytes = await file.read()

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(
            [
                {"mime_type": mime_type, "data": image_bytes},
                PROMPT,
            ]
        )
        text = (getattr(resp, "text", "") or "").strip()
        return JSONResponse(parse_output(text))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
