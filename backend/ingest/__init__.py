"""
OCR-based nutrition fact ingestion pipeline.
"""

from .ocr_reader import extract_text_from_image, extract_text_with_confidence
from .nutrition_parser import parse_nutrition_text, extract_product_name
from .clarify import (
    needs_clarification,
    get_clarification_form_data,
    merge_user_corrections,
    validate_nutrition_data
)

__all__ = [
    'extract_text_from_image',
    'extract_text_with_confidence',
    'parse_nutrition_text',
    'extract_product_name',
    'needs_clarification',
    'get_clarification_form_data',
    'merge_user_corrections',
    'validate_nutrition_data'
]
