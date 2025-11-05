"""
Response formatting utilities for consistent API responses.
"""

from typing import Dict, List, Optional


def format_evaluation_response(
    product: Dict,
    health_analysis: Dict,
    fitness_analysis: Dict,
    price_analysis: Dict,
    companion_message: str
) -> Dict:
    """
    Format a complete evaluation response with all analyses.

    Args:
        product: Product information
        health_analysis: Health evaluation results
        fitness_analysis: Fitness evaluation results
        price_analysis: Price evaluation results
        companion_message: AI companion message

    Returns:
        Formatted evaluation response
    """
    health_score = health_analysis.get('score', 0)
    fitness_score = fitness_analysis.get('score', 0)
    overall_score = (health_score + fitness_score) / 2

    recommendation, emoji = _get_recommendation(overall_score)

    return {
        'product': product,
        'health_analysis': health_analysis,
        'fitness_analysis': fitness_analysis,
        'price_analysis': price_analysis,
        'overall': {
            'score': round(overall_score, 1),
            'recommendation': recommendation,
            'recommendation_emoji': emoji
        },
        'companion_message': companion_message
    }


def format_error_response(error_message: str) -> Dict:
    """
    Format an error response.

    Args:
        error_message: Error message to include

    Returns:
        Formatted error response
    """
    return {
        'product': {},
        'health_analysis': _error_analysis('health'),
        'fitness_analysis': _error_analysis('fitness'),
        'price_analysis': _error_analysis('price'),
        'overall': {
            'score': 0,
            'recommendation': 'Error',
            'recommendation_emoji': '❌'
        },
        'companion_message': error_message,
        'error': True
    }


def _get_recommendation(score: float) -> tuple[str, str]:
    """Determine recommendation and emoji based on score."""
    if score >= 70:
        return "Highly Recommended", "✅"
    elif score >= 50:
        return "Acceptable with Caution", "⚠️"
    else:
        return "Not Recommended", "❌"


def _error_analysis(analysis_type: str) -> Dict:
    """Create error analysis response."""
    return {
        'score': 0,
        'summary': f'{analysis_type.title()} evaluation unavailable.',
        'error': True
    }


def format_product_dict(
    name: str,
    brand: str,
    category: str,
    price: float,
    size: Optional[str] = None,
    unit_price: Optional[float] = None,
    nutrition: Optional[Dict] = None,
    ingredients: Optional[str] = None
) -> Dict:
    """
    Format product information into a standardized dictionary.

    Args:
        name: Product name
        brand: Product brand
        category: Product category
        price: Product price
        size: Product size (optional)
        unit_price: Price per unit (optional)
        nutrition: Nutrition data (optional)
        ingredients: Ingredients list (optional)

    Returns:
        Formatted product dictionary
    """
    return {
        'name': name,
        'brand': brand,
        'category': category,
        'price': price,
        'size': size,
        'unit_price': unit_price,
        'nutrition': nutrition or {},
        'ingredients': ingredients
    }
