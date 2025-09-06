#!/usr/bin/env python3
"""
Enhanced receipt OCR with image preprocessing
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np

def preprocess_image(image_path):
    """Preprocess image for better OCR results"""
    try:
        # Load image with OpenCV
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply different preprocessing techniques
        processed_images = []
        
        # 1. Original grayscale
        processed_images.append(("Original Grayscale", gray))
        
        # 2. Gaussian blur + threshold
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        processed_images.append(("Gaussian Blur + OTSU", thresh))
        
        # 3. Adaptive threshold
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        processed_images.append(("Adaptive Threshold", adaptive))
        
        # 4. Morphological operations
        kernel = np.ones((1, 1), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed_images.append(("Morphological", morph))
        
        # 5. Denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        processed_images.append(("Denoised", denoised))
        
        return processed_images
        
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return []

def extract_text_with_config(image, config=''):
    """Extract text using different Tesseract configurations"""
    try:
        text = pytesseract.image_to_string(image, config=config)
        return text.strip()
    except Exception as e:
        print(f"Error with config '{config}': {e}")
        return ""

def convert_image_to_text_enhanced(image_path):
    """Convert image to text with enhanced preprocessing"""
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image file not found: {image_path}")
            return None
        
        print(f"Processing image: {image_path}")
        
        # Preprocess image
        processed_images = preprocess_image(image_path)
        
        if not processed_images:
            print("Failed to preprocess image")
            return None
        
        best_text = ""
        best_score = 0
        
        # Different OCR configurations to try
        configs = [
            '',  # Default
            '--psm 6',  # Assume a single uniform block of text
            '--psm 8',  # Treat the image as a single word
            '--psm 13', # Raw line. Treat the image as a single text line
            '--psm 6 --oem 3',  # Default OCR Engine Mode
            '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-$ ',
        ]
        
        results = []
        
        for name, processed_img in processed_images:
            print(f"\nTrying preprocessing: {name}")
            
            for config in configs:
                config_name = config if config else "default"
                text = extract_text_with_config(processed_img, config)
                
                if text:
                    # Simple scoring based on text length and character diversity
                    score = len(text) + len(set(text.lower())) * 2
                    
                    results.append({
                        'preprocessing': name,
                        'config': config_name,
                        'text': text,
                        'score': score,
                        'length': len(text)
                    })
                    
                    print(f"  Config '{config_name}': {len(text)} chars, score: {score}")
                    print(f"  Preview: {text[:100]}...")
                    
                    if score > best_score:
                        best_score = score
                        best_text = text
        
        # Sort results by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'best_text': best_text,
            'best_score': best_score,
            'all_results': results
        }
        
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
        print(f"\n{'='*80}")
        print(f"Processing: {image_file.name}")
        print(f"{'='*80}")
        
        # Convert image to text with enhanced processing
        result = convert_image_to_text_enhanced(str(image_file))
        
        if result and result['best_text']:
            print(f"\n{'='*80}")
            print("BEST RESULT:")
            print(f"{'='*80}")
            print(result['best_text'])
            print(f"\nScore: {result['best_score']}")
            
            # Save best result
            text_file = image_file.with_suffix('.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(result['best_text'])
            print(f"\nBest text saved to: {text_file}")
            
            # Save detailed results
            detailed_file = image_file.with_suffix('_detailed.txt')
            with open(detailed_file, 'w', encoding='utf-8') as f:
                f.write("OCR RESULTS SUMMARY\n")
                f.write("="*50 + "\n\n")
                f.write(f"Best Result (Score: {result['best_score']}):\n")
                f.write("-" * 30 + "\n")
                f.write(result['best_text'])
                f.write("\n\n")
                
                f.write("All Results:\n")
                f.write("-" * 30 + "\n")
                for i, res in enumerate(result['all_results'][:5], 1):
                    f.write(f"\n{i}. {res['preprocessing']} + {res['config']} (Score: {res['score']})\n")
                    f.write(f"   Length: {res['length']} chars\n")
                    f.write(f"   Text: {res['text'][:200]}...\n")
            
            print(f"Detailed results saved to: {detailed_file}")
        else:
            print("Failed to extract text from image")

if __name__ == "__main__":
    main()
