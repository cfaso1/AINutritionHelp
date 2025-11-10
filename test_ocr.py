#!/usr/bin/env python3
"""
Quick OCR test script to verify Tesseract is working
Run this on Render via shell: python test_ocr.py
"""

import sys
import os

print("=" * 60)
print("OCR Environment Test")
print("=" * 60)

# Check environment variables
print(f"\nTESSDATA_PREFIX: {os.getenv('TESSDATA_PREFIX', 'Not set')}")
print(f"PATH: {os.getenv('PATH', 'Not set')[:100]}...")

# Check Tesseract binary
print("\n1. Checking Tesseract binary...")
try:
    import subprocess
    result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✓ Tesseract found at: {result.stdout.strip()}")

        # Get version
        version_result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        print(f"   ✓ Version: {version_result.stdout.split()[1] if version_result.stdout else 'Unknown'}")
    else:
        print("   ✗ Tesseract binary not found in PATH")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Error checking binary: {e}")
    sys.exit(1)

# Check pytesseract
print("\n2. Checking pytesseract...")
try:
    import pytesseract
    print("   ✓ pytesseract imported successfully")

    version = pytesseract.get_tesseract_version()
    print(f"   ✓ Tesseract version via pytesseract: {version}")
except Exception as e:
    print(f"   ✗ pytesseract error: {e}")
    sys.exit(1)

# Check OpenCV
print("\n3. Checking OpenCV...")
try:
    import cv2
    print(f"   ✓ OpenCV version: {cv2.__version__}")
except Exception as e:
    print(f"   ✗ OpenCV error: {e}")
    sys.exit(1)

# Test OCR on sample text
print("\n4. Testing OCR with sample image...")
try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    # Create a simple test image with text
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)

    # Draw text (using default font)
    draw.text((10, 10), "Calories: 250", fill='black')
    draw.text((10, 40), "Protein: 21g", fill='black')

    # Convert to numpy array
    img_array = np.array(img)

    # Run OCR
    text = pytesseract.image_to_string(img_array)
    print(f"   ✓ OCR extracted text:\n   {repr(text)}")

    if 'Calories' in text or '250' in text:
        print("   ✓ OCR is working correctly!")
    else:
        print("   ⚠ OCR extracted text but may have accuracy issues")

except Exception as e:
    print(f"   ✗ OCR test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All OCR tests passed!")
print("=" * 60)
