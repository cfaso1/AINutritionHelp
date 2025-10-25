#!/usr/bin/env python3
"""
Barcode Detection from Images
Extracts barcode numbers from uploaded images using pyzbar and OpenCV.
"""

import cv2
import numpy as np
from PIL import Image
from pyzbar import pyzbar
from typing import Optional, List, Dict


def detect_barcodes_from_image(image_path: str) -> List[Dict[str, str]]:
    """
    Detect all barcodes in an image file.

    Args:
        image_path: Path to the image file

    Returns:
        List of dictionaries containing barcode data:
        [{'data': '123456789', 'type': 'EAN13', 'rect': (x, y, w, h)}]
    """
    try:
        # Read image
        image = cv2.imread(image_path)

        if image is None:
            # Try with PIL if OpenCV fails
            pil_image = Image.open(image_path)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale for better detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect barcodes
        barcodes = pyzbar.decode(gray)

        results = []
        for barcode in barcodes:
            # Extract barcode data
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type

            # Get rectangle coordinates
            rect = barcode.rect

            results.append({
                'data': barcode_data,
                'type': barcode_type,
                'rect': (rect.left, rect.top, rect.width, rect.height)
            })

        return results

    except Exception as e:
        print(f"Error detecting barcodes: {e}")
        return []


def extract_barcode_number(image_path: str) -> Optional[str]:
    """
    Extract the first barcode number found in an image.

    Args:
        image_path: Path to the image file

    Returns:
        Barcode number as string, or None if no barcode found
    """
    barcodes = detect_barcodes_from_image(image_path)

    if barcodes:
        return barcodes[0]['data']

    return None


def detect_barcodes_from_bytes(image_bytes: bytes) -> List[Dict[str, str]]:
    """
    Detect barcodes from image bytes (e.g., from file upload).

    Args:
        image_bytes: Image data as bytes

    Returns:
        List of detected barcodes
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return []

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect barcodes
        barcodes = pyzbar.decode(gray)

        results = []
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            rect = barcode.rect

            results.append({
                'data': barcode_data,
                'type': barcode_type,
                'rect': (rect.left, rect.top, rect.width, rect.height)
            })

        return results

    except Exception as e:
        print(f"Error detecting barcodes from bytes: {e}")
        return []


def extract_barcode_from_bytes(image_bytes: bytes) -> Optional[str]:
    """
    Extract the first barcode from image bytes.

    Args:
        image_bytes: Image data as bytes

    Returns:
        Barcode number as string, or None if no barcode found
    """
    barcodes = detect_barcodes_from_bytes(image_bytes)

    if barcodes:
        return barcodes[0]['data']

    return None


if __name__ == "__main__":
    # Test the barcode detector
    import sys

    if len(sys.argv) < 2:
        print("Usage: python barcode_detector.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    barcodes = detect_barcodes_from_image(image_path)

    if barcodes:
        print(f"Found {len(barcodes)} barcode(s):")
        for i, barcode in enumerate(barcodes, 1):
            print(f"  {i}. {barcode['type']}: {barcode['data']}")
            print(f"     Location: x={barcode['rect'][0]}, y={barcode['rect'][1]}")
    else:
        print("No barcodes detected in the image.")
