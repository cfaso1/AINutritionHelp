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
    Preprocess image to improve OCR accuracy.

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

    # Resize if image is too small (improves OCR)
    height, width = gray.shape
    if height < 300 or width < 300:
        scale = max(300 / height, 300 / width)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray)

    # Apply adaptive thresholding for better contrast
    thresh = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # Optional: dilation and erosion to clean up text
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Sharpen the image
    kernel_sharpen = np.array([[-1,-1,-1],
                               [-1, 9,-1],
                               [-1,-1,-1]])
    processed = cv2.filter2D(processed, -1, kernel_sharpen)

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
        # PSM modes: 3=fully automatic, 4=single column, 6=uniform block, 11=sparse text
        configs = [
            r'--oem 3 --psm 6',   # Single uniform block (best for labels)
            r'--oem 3 --psm 4',   # Single column of text
            r'--oem 3 --psm 3',   # Fully automatic page segmentation
            r'--oem 3 --psm 11',  # Sparse text (last resort)
        ]

        text = None
        best_text = ""

        for config in configs:
            try:
                extracted = pytesseract.image_to_string(processed, config=config)
                if extracted and len(extracted.strip()) > len(best_text):
                    best_text = extracted.strip()
                    if len(best_text) > 50:  # Good enough
                        break
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
