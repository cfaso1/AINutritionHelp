"""
Nutrition fact parser for extracting structured data from OCR text.
"""

import re
import logging
from typing import Dict, Tuple, Optional, Any

logger = logging.getLogger(__name__)

# Common unit variations and their standard forms
UNIT_PATTERNS = {
    'g': r'(?:grams?|g)',
    'mg': r'(?:milligrams?|mg)',
    'mcg': r'(?:micrograms?|mcg|µg|ug)',
    'serving': r'(?:servings?|srv)',
}


def normalize_units(value_str: str, unit_str: str) -> Tuple[float, str]:
    """
    Normalize value and unit to standard form.

    Args:
        value_str: Numeric value as string
        unit_str: Unit string

    Returns:
        Tuple of (normalized_value, normalized_unit)
    """
    try:
        value = float(value_str.replace(',', '').strip())
    except (ValueError, AttributeError):
        return 0.0, unit_str.lower()

    unit_lower = unit_str.lower().strip()

    # Standardize units
    if re.match(UNIT_PATTERNS['g'], unit_lower):
        return value, 'g'
    elif re.match(UNIT_PATTERNS['mg'], unit_lower):
        return value, 'mg'
    elif re.match(UNIT_PATTERNS['mcg'], unit_lower):
        return value, 'mcg'

    return value, unit_lower


def extract_numeric_value(text: str) -> Optional[float]:
    """
    Extract first numeric value from text string.

    Args:
        text: Input text

    Returns:
        Float value or None if no number found
    """
    # Match numbers including decimals
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def find_nutrition_field(text: str, field_patterns: list, unit_required: bool = True) -> Tuple[Optional[float], Optional[str], float]:
    """
    Find nutrition field value using multiple regex patterns.

    Args:
        text: OCR text to search
        field_patterns: List of regex patterns to try
        unit_required: Whether unit is required for confidence

    Returns:
        Tuple of (value, unit, confidence_score)
    """
    for pattern in field_patterns:
        # Search case-insensitive, multiline
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            groups = match.groups()

            # Extract value
            value_str = groups[0] if groups else None
            if not value_str:
                continue

            value = extract_numeric_value(value_str)
            if value is None:
                continue

            # Extract unit if present
            unit = groups[1].strip() if len(groups) > 1 and groups[1] else None

            # Calculate confidence based on pattern match quality
            confidence = 0.9  # High confidence for direct pattern match

            if unit:
                normalized_value, normalized_unit = normalize_units(str(value), unit)
                return normalized_value, normalized_unit, confidence
            elif not unit_required:
                return value, None, confidence
            else:
                # Found number but no unit, lower confidence
                return value, None, 0.6

    return None, None, 0.0


def parse_nutrition_text(text: str) -> Dict[str, Any]:
    """
    Parse nutrition facts from OCR text using regex patterns.

    Args:
        text: OCR extracted text

    Returns:
        Dictionary with 'data' (nutrition values) and 'confidences' (per-field confidence)
    """
    logger.info("Parsing nutrition text")
    logger.debug(f"Raw text to parse: {text}")

    data = {}
    confidences = {}

    # Priority fields with multiple pattern variations (more flexible now)

    # Optional: Calories (prioritize this)
    calorie_patterns = [
        r'Calories[:\s-]*(\d+(?:\.\d+)?)',
        r'Energy[:\s-]*(\d+(?:\.\d+)?)',
        r'(?:^|\n)(\d+)\s*(?:cal|kcal)',
    ]
    value, _, conf = find_nutrition_field(text, calorie_patterns, unit_required=False)
    if value is not None:
        data['calories'] = value
        confidences['calories'] = conf

    # Protein (more flexible patterns)
    protein_patterns = [
        r'Protein[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Prot[.\s:]*(\d+(?:\.\d+)?)\s*(g)?',
        r'(?:^|\n)Protein.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, protein_patterns, unit_required=False)
    if value is not None:
        data['protein'] = value
        confidences['protein'] = conf

    # Total Carbohydrates (more flexible)
    carbs_patterns = [
        r'Total\s+Carbohydrate[s]?[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Carbohydrate[s]?[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Carbs?[:\s-]*(\d+(?:\.\d+)?)\s*(g)?',
        r'(?:^|\n)Carb.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, carbs_patterns, unit_required=False)
    if value is not None:
        data['carbs_total'] = value
        confidences['carbs_total'] = conf

    # Sugar (more flexible)
    sugar_patterns = [
        r'Total\s+Sugars?[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Sugars?,?\s+Total[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Sugars?[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'(?:^|\n)Sugar.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, sugar_patterns, unit_required=False)
    if value is not None:
        data['sugar_total'] = value
        confidences['sugar_total'] = conf

    # Total Fat (more flexible)
    fat_patterns = [
        r'Total\s+Fat[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Fat,?\s+Total[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Fat[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'(?:^|\n)Fat.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, fat_patterns, unit_required=False)
    if value is not None:
        data['fat_total'] = value
        confidences['fat_total'] = conf

    # Sodium (more flexible)
    sodium_patterns = [
        r'Sodium[:\s-]*(\d+(?:\.\d+)?)\s*(mg|milligrams?)?',
        r'Na[:\s-]*(\d+(?:\.\d+)?)\s*(mg)?',
        r'Salt[:\s-]*(\d+(?:\.\d+)?)\s*(mg)?',
        r'(?:^|\n)Sodium.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, sodium_patterns, unit_required=False)
    if value is not None:
        data['sodium'] = value
        confidences['sodium'] = conf

    # Cholesterol (more flexible)
    cholesterol_patterns = [
        r'Cholesterol[:\s-]*(\d+(?:\.\d+)?)\s*(mg|milligrams?)?',
        r'Chol[.\s:]*(\d+(?:\.\d+)?)\s*(mg)?',
        r'(?:^|\n)Cholesterol.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, cholesterol_patterns, unit_required=False)
    if value is not None:
        data['cholesterol'] = value
        confidences['cholesterol'] = conf

    # Serving Size (more flexible)
    serving_patterns = [
        r'Serving\s+Size[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?|oz|ml|cup|cups?|pieces?|items?)?',
        r'Serv[.\s]+Size[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?|oz|ml)?',
        r'Per\s+Serving[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'(?:^|\n)Serving.*?(\d+(?:\.\d+)?)\s*(g|oz)?',
    ]
    value, unit, conf = find_nutrition_field(text, serving_patterns, unit_required=False)
    if value is not None:
        data['serving_size'] = f"{value}{unit if unit else 'g'}"
        confidences['serving_size'] = conf if unit else conf * 0.7

    # Servings Per Container (more flexible)
    servings_per_patterns = [
        r'Servings?\s+[Pp]er\s+Container[:\s-]*(\d+(?:\.\d+)?)',
        r'Servings?[:\s-]*(\d+(?:\.\d+)?)',
        r'Container[:\s-]*(\d+(?:\.\d+)?)\s*servings?',
        r'(?:^|\n).*?(\d+)\s*servings?',
    ]
    value, _, conf = find_nutrition_field(text, servings_per_patterns, unit_required=False)
    if value is not None:
        data['servings_per_container'] = value
        confidences['servings_per_container'] = conf

    # Optional: Saturated Fat (more flexible)
    sat_fat_patterns = [
        r'Saturated\s+Fat[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Sat[.\s]+Fat[:\s-]*(\d+(?:\.\d+)?)\s*(g)?',
        r'(?:^|\n)Saturated.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, sat_fat_patterns, unit_required=False)
    if value is not None:
        data['saturated_fat'] = value
        confidences['saturated_fat'] = conf

    # Optional: Trans Fat (more flexible)
    trans_fat_patterns = [
        r'Trans\s+Fat[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Trans[.\s]+Fat[:\s-]*(\d+(?:\.\d+)?)\s*(g)?',
        r'(?:^|\n)Trans.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, trans_fat_patterns, unit_required=False)
    if value is not None:
        data['trans_fat'] = value
        confidences['trans_fat'] = conf

    # Optional: Dietary Fiber (more flexible)
    fiber_patterns = [
        r'Dietary\s+Fiber[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'Fiber[:\s-]*(\d+(?:\.\d+)?)\s*(g|grams?)?',
        r'(?:^|\n)Fiber.*?(\d+(?:\.\d+)?)',
    ]
    value, unit, conf = find_nutrition_field(text, fiber_patterns, unit_required=False)
    if value is not None:
        data['dietary_fiber'] = value
        confidences['dietary_fiber'] = conf

    # Extract ingredients list (if present)
    ingredients_match = re.search(
        r'INGREDIENTS?[:\s]+([A-Za-z0-9,\s\(\)\.\-]+?)(?=\n\n|NUTRITION|ALLERGEN|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if ingredients_match:
        ingredients_text = ingredients_match.group(1).strip()
        data['ingredients'] = ingredients_text
        confidences['ingredients'] = 0.8

    logger.info(f"Parsed {len(data)} nutrition fields with average confidence {sum(confidences.values())/len(confidences) if confidences else 0:.2f}")

    return {
        'data': data,
        'confidences': confidences
    }


def extract_product_name(text: str) -> Optional[str]:
    """
    Attempt to extract product name from nutrition label text.

    Args:
        text: OCR text

    Returns:
        Product name if found, None otherwise
    """
    # Product name is typically at the top, before "Nutrition Facts"
    lines = text.split('\n')

    for i, line in enumerate(lines[:5]):  # Check first 5 lines
        line_clean = line.strip()
        if len(line_clean) > 3 and not re.search(r'nutrition|facts|label', line_clean, re.IGNORECASE):
            # Likely a product name
            if not re.search(r'\d+\s*(g|mg|calories|serving)', line_clean, re.IGNORECASE):
                return line_clean

    return None
