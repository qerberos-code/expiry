#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, sys, time
from pathlib import Path
from typing import Iterable, List, Dict, Any, Tuple, Optional

# --- LangChain / Ollama ---
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult
# --- Utils ---
from PIL import Image, UnidentifiedImageError
import mimetypes
from rapidfuzz import fuzz

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg"}

SYSTEM_INSTRUCTIONS = (
    "You are an expert receipt detector and extractor. "
    "Given ONE image, respond ONLY in compact JSON format without any Markdown formatting. "
    'Schema: {"is_receipt": true|false, "vendor": string|null, "date": string|null, "total": string|null, "notes": string|null}. '
    "If not a receipt, set is_receipt=false and others=null. "
    "If a receipt, be concise; date in ISO if visible (YYYY-MM-DD if you can), total with currency symbol if visible. "
    "DO NOT USE MARKDOWN FORMATTING. RETURN ONLY VALID JSON."
)

USER_ASK = (
    "Is this image a receipt? If yes, return vendor, date, and total. "
    "If unsure, pick false unless the layout clearly resembles a receipt."
)

def is_image_file(path: Path) -> bool:
    # Only allow extensions that are explicitly in SUPPORTED_EXTS
    # No fallback to MIME type detection
    return path.suffix.lower() in SUPPORTED_EXTS

def quick_image_openable(path: Path, max_side: int = 2200) -> Tuple[bool, Optional[Path]]:
    """Try opening & (optionally) downscaling giant images to keep VRAM sane.
    Returns (ok, possibly_tempfile_path_or_None). If we resized, return the temp path; else None."""
    try:
        with Image.open(path) as im:
            im.verify()  # lightweight check
        # Re-open to actually resize if needed
        with Image.open(path) as im2:
            w, h = im2.size
            if max(w, h) <= max_side:
                return True, None
            scale = max_side / float(max(w, h))
            new_size = (int(w * scale), int(h * scale))
            im2 = im2.convert("RGB").resize(new_size)
            temp = path.with_suffix(".thumb.jpg")
            im2.save(temp, "JPEG", quality=90, optimize=True)
            return True, temp
    except UnidentifiedImageError:
        return False, None
    except Exception:
        # If anything odd, skip gracefully
        return False, None

def force_json(text: str) -> Dict[str, Any]:
    """Tolerant JSON extraction: find the first {...} block and parse."""
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    
    # Try bracket capture
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    
    # Enhanced parser for markdown/formatted text responses
    result = {
        "is_receipt": False,
        "vendor": None,
        "date": None,
        "total": None,
        "notes": text.strip()[:300]
    }
    
    # First, check if the model explicitly says it's a receipt
    t = text.lower()
    receipt_indicators = ["is this image a receipt?: yes", "is a receipt", "this is a receipt", "receipt detected"]
    not_receipt_indicators = ["not a receipt", "isn't a receipt", "is not a receipt"]
    
    # Check for receipt indicators
    is_receipt = any(indicator in t for indicator in receipt_indicators)
    # Check for non-receipt indicators (with higher priority)
    is_not_receipt = any(indicator in t for indicator in not_receipt_indicators)
    
    # Set receipt status based on indicators
    if is_receipt and not is_not_receipt:
        result["is_receipt"] = True
    
    # Extract date if present
    date_match = re.search(r"date[^\w]?\s*:?\s*([0-9/-]+)", t, re.IGNORECASE)
    if date_match:
        result["date"] = date_match.group(1).strip()
    
    # Extract total if present (with currency symbols)
    total_match = re.search(r"total[^\w]?\s*:?\s*([$€£¥]?\s*\d+[.,]\d+|\d+[.,]\d+\s*[$€£¥]?)", t, re.IGNORECASE)
    if total_match:
        result["total"] = total_match.group(1).strip()
    
    # Extract vendor if present
    vendor_match = re.search(r"vendor[^\w]?\s*:?\s*([^,\n\r]*)", t, re.IGNORECASE)
    if vendor_match and vendor_match.group(1).strip().lower() not in ["not specified", "none", "null", "n/a"]:
        result["vendor"] = vendor_match.group(1).strip()
    
    # Print what we extracted for debugging
    print(f"Extracted from model response: {result}")
    
    return result

def check_one_image(chat: ChatOllama, img_path: Path) -> Dict[str, Any]:
    ok, maybe_resized = quick_image_openable(img_path)
    if not ok:
        return {
            "path": str(img_path),
            "is_receipt": False,
            "vendor": None, "date": None, "total": None,
            "notes": "Unreadable or not an image"
        }
    use_path = maybe_resized or img_path
    
    # Convert image to base64 manually instead of using as_uri
    import base64
    try:
        with open(use_path, "rb") as image_file:
            image_bytes = image_file.read()
            # For debugging
            print(f"Image size: {len(image_bytes)} bytes")
            
            # Check image format and convert if needed
            from PIL import Image
            import io
            
            # Convert to standard format (JPEG)
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Convert to RGB if needed (removes alpha channel)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Save to bytes
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG")
                image_bytes = buffer.getvalue()
            
            # Encode to base64
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            
            messages = [
                SystemMessage(content=SYSTEM_INSTRUCTIONS),
                HumanMessage(content=[
                    {"type": "text", "text": USER_ASK},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64_image}"},
                ]),
            ]
            
            resp: ChatResult = chat.invoke(messages)
            parsed = force_json(resp.content if isinstance(resp.content, str) else str(resp.content))
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error processing {img_path}: {error_details}")
        parsed = {"is_receipt": False, "vendor": None, "date": None, "total": None, "notes": f"LLM error: {e}"}
    
    # cleanup thumb
    if maybe_resized and maybe_resized.exists():
        try: maybe_resized.unlink()
        except Exception: pass
    
    parsed["path"] = str(img_path)
    return parsed

def iter_images(root: Path) -> Iterable[Path]:
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.name.startswith(".") and is_image_file(p):
            yield p

def scan_images():
    ap = argparse.ArgumentParser(description="Scan Downloads for receipts with an Ollama vision model via LangChain.")
    ap.add_argument("--folder", default=str(Path.home() / "Downloads"), help="Folder to scan (default: ~/Downloads)")
    ap.add_argument("--model", default="llama3.2-vision", help="Ollama model name (e.g., llama3.2-vision or llava)")
    ap.add_argument("--num-ctx", type=int, default=4096, help="Ollama context tokens")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-side", type=int, default=2200, help="Downscale images whose longest side exceeds this")
    ap.add_argument("--limit", type=int, default=0, help="Process only N images (for testing). 0 = no limit")
    ap.add_argument("--out-jsonl", default="receipts_scan.jsonl")
    ap.add_argument("--out-csv", default="receipts_scan.csv")
    args = ap.parse_args()

    root = Path(args.folder).expanduser()
    if not root.exists():
        print(f"Folder not found: {root}", file=sys.stderr)
        sys.exit(2)

    chat = ChatOllama(
        model=args.model,
        temperature=args.temperature,
        num_ctx=args.num_ctx
    )

    results: List[Dict[str, Any]] = []
    count = 0

    for img in iter_images(root):
        if args.limit and count >= args.limit:
            break
        # Update global max_side for resizing
        global SUPPORTED_EXTS
        parsed = check_one_image(chat, img)
        results.append(parsed)
        count += 1
        print(f"[{count}] {img.name}: is_receipt={parsed.get('is_receipt')} vendor={parsed.get('vendor')} date={parsed.get('date')} total={parsed.get('total')}")

    # Write JSONL
    with open(args.out_jsonl, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    yes = [r for r in results if r.get("is_receipt")]
    print(f"\nScanned {len(results)} images in {root}")
    print(f"Receipts detected: {len(yes)}")
    if yes:
        print("Sample:")
        for r in yes[:5]:
            print(f"- {Path(r['path']).name}: vendor={r.get('vendor')} date={r.get('date')} total={r.get('total')}")

if __name__ == "__main__":
    scan_images()
