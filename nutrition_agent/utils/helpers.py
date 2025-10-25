"""
Helper utility functions for the nutrition agent system
"""
from typing import Dict, Any, List


def format_currency(amount: float) -> str:
    """Format a number as currency"""
    return f"${amount:.2f}"


def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage safely"""
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def parse_nutrition_value(value: Any) -> float:
    """Safely parse nutrition values"""
    try:
        if isinstance(value, str):
            # Remove units and non-numeric characters except decimal
            value = ''.join(c for c in value if c.isdigit() or c == '.')
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def normalize_goal(goal: str) -> str:
    """Normalize user goal text"""
    return goal.strip().lower().replace("_", " ")


def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """Extract matching keywords from text"""
    text_lower = text.lower()
    found = []
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
    return found


def score_to_color(score: int) -> str:
    """Convert score to color code"""
    if score >= 70:
        return "green"
    elif score >= 40:
        return "yellow"
    else:
        return "red"


def score_to_rating(score: int) -> str:
    """Convert numeric score to text rating"""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Very Good"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"
