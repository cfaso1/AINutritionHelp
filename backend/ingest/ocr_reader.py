"""
OCR reader for extracting text from nutrition fact images using Tesseract.
"""

import logging
from typing import Union
from pathlib import Path
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

    # Optional: dilation and erosion to connect broken characters
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

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

        # Configure Tesseract for nutrition labels
        # PSM 6: Assume a single uniform block of text
        # PSM 11: Sparse text. Find as much text as possible in no particular order
        custom_config = r'--oem 3 --psm 6'

        # Extract text
        text = pytesseract.image_to_string(processed, config=custom_config)

        if not text or not text.strip():
            # Try alternative PSM mode if first attempt fails
            logger.info("First OCR attempt returned empty, trying alternative mode")
            custom_config = r'--oem 3 --psm 11'
            text = pytesseract.image_to_string(processed, config=custom_config)

        logger.info(f"OCR extracted {len(text)} characters")
        logger.debug(f"OCR text: {text[:200]}...")  # Log first 200 chars

        return text.strip()

    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract not found. Please install tesseract-ocr")
        raise RuntimeError(
            "Tesseract OCR is not installed. "
            "Install it with: sudo apt-get install tesseract-ocr (Linux) "
            "or brew install tesseract (Mac)"
        )
    except Exception as e:
        logger.error(f"OCR failed: {e}")
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
