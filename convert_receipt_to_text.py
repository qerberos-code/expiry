#!/usr/bin/env python3
"""
Convert receipt images to text using OCR
"""

import os
import sys
from pathlib import Path
from PIL import Image
import pytesseract

def convert_image_to_text(image_path):
    """Convert image to text using Tesseract OCR"""
    try:
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"Error: Image file not found: {image_path}")
            return None
        
        # Open and process image
        with Image.open(image_path) as img:
            print(f"Processing image: {image_path}")
            print(f"Image size: {img.size}")
            print(f"Image mode: {img.mode}")
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Use Tesseract OCR to extract text
            text = pytesseract.image_to_string(img)
            
            return text
            
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def main():
    """Main function to process receipt images"""
    receipts_dir = Path("receipts")
    
    if not receipts_dir.exists():
        print("Receipts directory not found!")
        return
    
    # Find all image files
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        image_files.extend(receipts_dir.glob(f"*{ext}"))
        image_files.extend(receipts_dir.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print("No image files found in receipts directory!")
        return
    
    print(f"Found {len(image_files)} image file(s)")
    
    for image_file in image_files:
        print(f"\n{'='*60}")
        print(f"Processing: {image_file.name}")
        print(f"{'='*60}")
        
        # Convert image to text
        text = convert_image_to_text(str(image_file))
        
        if text:
            print(f"\nExtracted Text:")
            print(f"{'-'*40}")
            print(text)
            print(f"{'-'*40}")
            
            # Save text to file
            text_file = image_file.with_suffix('.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\nText saved to: {text_file}")
        else:
            print("Failed to extract text from image")

if __name__ == "__main__":
    main()
