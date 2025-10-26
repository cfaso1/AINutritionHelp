"""
Data parsing utilities for nutrition information.
"""

from typing import Dict, Optional


def parse_nutrition_data(raw_data: Dict) -> Dict[str, float]:
    """
    Parse and normalize nutrition data from various sources.

    Args:
        raw_data: Raw nutrition data dictionary

    Returns:
        Normalized nutrition data with standard keys
    """
    nutrition = {}

    # Standard nutrition fields
    fields = {
        'calories': ['calories', 'energy', 'kcal'],
        'protein': ['protein', 'proteins'],
        'carbohydrates': ['carbohydrates', 'carbs', 'total_carbohydrate'],
        'sugar': ['sugar', 'sugars', 'total_sugars'],
        'fat': ['fat', 'total_fat', 'fats'],
        'saturated_fat': ['saturated_fat', 'sat_fat'],
        'sodium': ['sodium', 'salt'],
        'fiber': ['fiber', 'dietary_fiber', 'fibre'],
    }

    for standard_key, possible_keys in fields.items():
        for key in possible_keys:
            if key in raw_data:
                nutrition[standard_key] = _parse_float(raw_data[key])
                break
        if standard_key not in nutrition:
            nutrition[standard_key] = 0.0

    return nutrition


def calculate_macros(protein: float, carbs: float, fat: float) -> Dict[str, float]:
    """
    Calculate macronutrient percentages from gram amounts.

    Args:
        protein: Protein in grams
        carbs: Carbohydrates in grams
        fat: Fat in grams

    Returns:
        Dictionary with protein_percent, carb_percent, fat_percent
    """
    # Calculate calories from macros (protein: 4cal/g, carbs: 4cal/g, fat: 9cal/g)
    total_calories = (protein * 4) + (carbs * 4) + (fat * 9)

    if total_calories == 0:
        return {
            'protein_percent': 0.0,
            'carb_percent': 0.0,
            'fat_percent': 0.0,
            'total_calories': 0.0
        }

    return {
        'protein_percent': (protein * 4 / total_calories) * 100,
        'carb_percent': (carbs * 4 / total_calories) * 100,
        'fat_percent': (fat * 9 / total_calories) * 100,
        'total_calories': total_calories
    }


def _parse_float(value) -> float:
    """Safely parse a value to float."""
    try:
        if isinstance(value, str):
            value = ''.join(c for c in value if c.isdigit() or c == '.')
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0


def extract_nutrition_value(nutrition: Optional[Dict], key: str, default: float = 0.0) -> float:
    """
    Safely extract a nutrition value from a dictionary.

    Args:
        nutrition: Nutrition data dictionary
        key: Key to extract
        default: Default value if not found

    Returns:
        Nutrition value as float
    """
    if not nutrition:
        return default
    return nutrition.get(key, default)
