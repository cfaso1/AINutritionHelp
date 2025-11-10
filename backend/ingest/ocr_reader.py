"""
OCR reader for extracting text from nutrition fact images using Tesseract.
"""

import logging
from typing import Union
from pathlib import Path
import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import io

logger = logging.getLogger(__name__)


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image to improve OCR accuracy for nutrition labels.

    Args:
        image: Input image as numpy array

    Returns:
        Preprocessed image
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Resize if image is too small - nutrition labels need higher resolution
    height, width = gray.shape
    if height < 800 or width < 600:
        scale = max(800 / height, 600 / width)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # For very large images, resize down to avoid excessive processing
    elif height > 3000 or width > 3000:
        scale = min(3000 / height, 3000 / width)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # Apply bilateral filter to reduce noise while preserving edges
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)

    # Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(filtered)

    # Apply Otsu's thresholding for better binarization
    _, binary = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Remove noise with morphological operations
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel, iterations=1)

    return processed


def extract_text_from_image(image_input: Union[bytes, str, Path]) -> str:
    """
    Extract text from nutrition facts image using Tesseract OCR.

    Args:
        image_input: Can be image bytes, file path string, or Path object

    Returns:
        Extracted text as string

    Raises:
        ValueError: If image cannot be processed
        RuntimeError: If Tesseract is not installed or fails
    """
    try:
        # Load image based on input type
        if isinstance(image_input, bytes):
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_input))
            # Convert to numpy array for OpenCV
            img_array = np.array(image)
        elif isinstance(image_input, (str, Path)):
            # Load from file path
            img_array = cv2.imread(str(image_input))
            if img_array is None:
                raise ValueError(f"Could not load image from {image_input}")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        # Preprocess image
        processed = preprocess_image(img_array)

        # Try multiple OCR configurations for best results
        # PSM modes:
        # 3=fully automatic, 4=single column, 6=uniform block, 11=sparse text, 12=sparse text + OSD
        # Added custom whitelist for nutrition labels
        configs = [
            r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz%.,()/:- ',
            r'--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz%.,()/:- ',
            r'--oem 3 --psm 6',   # Single uniform block (best for labels)
            r'--oem 3 --psm 3',   # Fully automatic page segmentation
        ]

        text = None
        best_text = ""
        best_length = 0

        for config in configs:
            try:
                # Try on preprocessed image
                extracted = pytesseract.image_to_string(processed, config=config)
                if extracted and len(extracted.strip()) > best_length:
                    best_text = extracted.strip()
                    best_length = len(best_text)
                    logger.debug(f"Config '{config}' extracted {best_length} chars")

                # If we get a good amount of text, also try on original grayscale
                if best_length < 100:
                    if len(img_array.shape) == 3:
                        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = img_array
                    extracted_gray = pytesseract.image_to_string(gray, config=config)
                    if len(extracted_gray.strip()) > best_length:
                        best_text = extracted_gray.strip()
                        best_length = len(best_text)
                        logger.debug(f"Config '{config}' on grayscale extracted {best_length} chars")

            except Exception as e:
                logger.debug(f"OCR config {config} failed: {e}")
                continue

        text = best_text

        logger.info(f"OCR extracted {len(text)} characters")
        logger.info(f"OCR text preview: {text[:300] if len(text) <= 300 else text[:300] + '...'}")

        return text.strip()

    except pytesseract.TesseractNotFoundError as e:
        logger.error(f"Tesseract not found: {e}")
        logger.error("TESSDATA_PREFIX: " + os.getenv("TESSDATA_PREFIX", "Not set"))
        logger.error("PATH: " + os.getenv("PATH", "Not set"))
        raise RuntimeError(
            "Tesseract OCR is not installed or not in PATH. "
            "Install it with: sudo apt-get install tesseract-ocr (Linux) "
            "or brew install tesseract (Mac)"
        )
    except Exception as e:
        logger.error(f"OCR failed: {e}", exc_info=True)
        logger.error(f"Image input type: {type(image_input)}")
        logger.error(f"Image shape: {img_array.shape if 'img_array' in locals() else 'Not loaded'}")
        raise ValueError(f"Failed to extract text from image: {str(e)}")


def extract_text_with_confidence(image_input: Union[bytes, str, Path]) -> tuple[str, dict]:
    """
    Extract text with per-word confidence scores.

    Args:
        image_input: Can be image bytes, file path string, or Path object

    Returns:
        Tuple of (full_text, confidence_data_dict)
    """
    try:
        # Load and preprocess image (same as above)
        if isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
            img_array = np.array(image)
        elif isinstance(image_input, (str, Path)):
            img_array = cv2.imread(str(image_input))
            if img_array is None:
                raise ValueError(f"Could not load image from {image_input}")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        processed = preprocess_image(img_array)

        # Get detailed OCR data with confidence
        custom_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_data(processed, config=custom_config, output_type=pytesseract.Output.DICT)

        # Calculate average confidence
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Extract full text
        text = pytesseract.image_to_string(processed, config=custom_config).strip()

        confidence_data = {
            'average': avg_confidence / 100.0,  # Normalize to 0-1
            'word_count': len([w for w in data['text'] if w.strip()]),
            'low_confidence_words': [
                data['text'][i] for i in range(len(data['text']))
                if data['text'][i].strip() and int(data['conf'][i]) < 60
            ]
        }

        return text, confidence_data

    except Exception as e:
        logger.error(f"OCR with confidence failed: {e}")
        # Fallback to simple extraction
        text = extract_text_from_image(image_input)
        return text, {'average': 0.5, 'word_count': 0, 'low_confidence_words': []}
