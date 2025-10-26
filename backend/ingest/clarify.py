"""
Clarification module for detecting missing or low-confidence nutrition data.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Priority fields that should always be present
PRIORITY_FIELDS = [
    'fat_total',
    'sugar_total',
    'sodium',
    'carbs_total',
    'protein',
    'cholesterol',
    'serving_size',
    'servings_per_container'
]

# Field display names for user prompts
FIELD_DISPLAY_NAMES = {
    'fat_total': 'Total Fat (g)',
    'sugar_total': 'Total Sugar (g)',
    'sodium': 'Sodium (mg)',
    'carbs_total': 'Total Carbohydrates (g)',
    'protein': 'Protein (g)',
    'cholesterol': 'Cholesterol (mg)',
    'serving_size': 'Serving Size',
    'servings_per_container': 'Servings Per Container',
    'calories': 'Calories',
    'saturated_fat': 'Saturated Fat (g)',
    'trans_fat': 'Trans Fat (g)',
    'dietary_fiber': 'Dietary Fiber (g)',
}

# Confidence threshold below which we ask for clarification
CONFIDENCE_THRESHOLD = 0.7


def needs_clarification(data: Dict[str, Any], confidences: Dict[str, float]) -> Dict[str, Any]:
    """
    Determine if parsed nutrition data needs user clarification.

    Args:
        data: Parsed nutrition data dictionary
        confidences: Per-field confidence scores

    Returns:
        Dictionary with:
        - needs_clarification: bool
        - missing_fields: list of missing priority field names
        - low_confidence_fields: list of fields with confidence below threshold
        - prompt_message: str with user-friendly message
    """
    logger.info("Checking if clarification needed")

    missing_fields = []
    low_confidence_fields = []

    # Check for missing priority fields
    for field in PRIORITY_FIELDS:
        if field not in data or data[field] is None:
            missing_fields.append(field)
        elif field in confidences and confidences[field] < CONFIDENCE_THRESHOLD:
            low_confidence_fields.append(field)

    needs_clarify = bool(missing_fields or low_confidence_fields)

    # Build user-friendly prompt message
    prompt_message = ""
    if missing_fields:
        missing_display = [FIELD_DISPLAY_NAMES.get(f, f) for f in missing_fields]
        prompt_message += f"Missing fields: {', '.join(missing_display)}. "

    if low_confidence_fields:
        low_conf_display = [
            f"{FIELD_DISPLAY_NAMES.get(f, f)} ({confidences[f]:.0%} confidence)"
            for f in low_confidence_fields
        ]
        prompt_message += f"Low confidence: {', '.join(low_conf_display)}. "

    if needs_clarify:
        prompt_message += "Please verify or manually enter these values."

    logger.info(f"Clarification needed: {needs_clarify}, missing: {len(missing_fields)}, low conf: {len(low_confidence_fields)}")

    return {
        'needs_clarification': needs_clarify,
        'missing_fields': missing_fields,
        'low_confidence_fields': low_confidence_fields,
        'prompt_message': prompt_message
    }


def get_clarification_form_data(data: Dict[str, Any], confidences: Dict[str, float]) -> Dict[str, Any]:
    """
    Generate form data for clarification UI.

    Args:
        data: Parsed nutrition data
        confidences: Per-field confidence scores

    Returns:
        Dictionary with fields that need clarification and their current values
    """
    clarification_info = needs_clarification(data, confidences)

    if not clarification_info['needs_clarification']:
        return {}

    form_fields = {}

    # Include missing fields with empty values
    for field in clarification_info['missing_fields']:
        form_fields[field] = {
            'value': None,
            'display_name': FIELD_DISPLAY_NAMES.get(field, field),
            'confidence': 0.0,
            'status': 'missing'
        }

    # Include low confidence fields with extracted values
    for field in clarification_info['low_confidence_fields']:
        form_fields[field] = {
            'value': data.get(field),
            'display_name': FIELD_DISPLAY_NAMES.get(field, field),
            'confidence': confidences.get(field, 0.0),
            'status': 'low_confidence'
        }

    return form_fields


def merge_user_corrections(
    original_data: Dict[str, Any],
    user_corrections: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge user-provided corrections with original parsed data.

    Args:
        original_data: Original parsed data
        user_corrections: User-provided corrections

    Returns:
        Merged data dictionary with user corrections taking precedence
    """
    merged = original_data.copy()

    for field, value in user_corrections.items():
        if value is not None and value != '':
            # Convert numeric strings to floats for numeric fields
            if field in ['fat_total', 'sugar_total', 'sodium', 'carbs_total',
                        'protein', 'cholesterol', 'calories', 'saturated_fat',
                        'trans_fat', 'dietary_fiber', 'servings_per_container']:
                try:
                    merged[field] = float(value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {field} value '{value}' to float")
                    merged[field] = value
            else:
                merged[field] = value

    logger.info(f"Merged {len(user_corrections)} user corrections into data")

    return merged


def validate_nutrition_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate nutrition data for basic sanity checks.

    Args:
        data: Nutrition data to validate

    Returns:
        Dictionary with:
        - valid: bool
        - errors: list of validation error messages
    """
    errors = []

    # Check for required priority fields
    for field in PRIORITY_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {FIELD_DISPLAY_NAMES.get(field, field)}")

    # Sanity checks for numeric values
    numeric_fields = ['fat_total', 'sugar_total', 'sodium', 'carbs_total',
                     'protein', 'cholesterol', 'calories', 'servings_per_container']

    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                value = float(data[field])
                if value < 0:
                    errors.append(f"{FIELD_DISPLAY_NAMES.get(field, field)} cannot be negative")
                if value > 10000:  # Sanity upper limit
                    errors.append(f"{FIELD_DISPLAY_NAMES.get(field, field)} seems unusually high ({value})")
            except (ValueError, TypeError):
                errors.append(f"{FIELD_DISPLAY_NAMES.get(field, field)} must be a number")

    # Validate serving size format
    if 'serving_size' in data and data['serving_size']:
        serving = str(data['serving_size'])
        if not any(char.isdigit() for char in serving):
            errors.append("Serving size must contain a numeric value")

    is_valid = len(errors) == 0

    logger.info(f"Validation result: {'valid' if is_valid else f'{len(errors)} errors'}")

    return {
        'valid': is_valid,
        'errors': errors
    }
