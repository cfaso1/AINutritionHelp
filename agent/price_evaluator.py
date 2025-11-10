"""
Price Evaluator - Analyzes product pricing and value for money.
"""

import os
from typing import Dict
from google import genai
from dotenv import load_dotenv

from agent.models import Product

load_dotenv()


class PriceEvaluator:
    """
    Evaluates product pricing and provides value-for-money analysis.

    Compares prices against category averages and provides budget-friendly
    recommendations.
    """

    # Category average prices (per unit)
    CATEGORY_BENCHMARKS = {
        "snacks": {"low": 0.10, "avg": 0.20, "high": 0.35},
        "beverages": {"low": 0.05, "avg": 0.12, "high": 0.25},
        "dairy": {"low": 0.15, "avg": 0.30, "high": 0.50},
        "cereals": {"low": 0.12, "avg": 0.25, "high": 0.40},
        "breakfast": {"low": 0.12, "avg": 0.25, "high": 0.40},
        "frozen": {"low": 0.20, "avg": 0.35, "high": 0.55},
        "health_food": {"low": 0.30, "avg": 0.50, "high": 0.80},
        "default": {"low": 0.10, "avg": 0.25, "high": 0.45},
    }

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Price Evaluator with AI model."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def evaluate(self, product: Product) -> Dict:
        """
        Evaluate product pricing.

        Args:
            product: Product to evaluate

        Returns:
            Price analysis with rating, value assessment, and summary
        """
        # Check if price is available
        if not product.price:
            return {
                "is_good_deal": None,
                "rating": "No Price Data",
                "unit_price": None,
                "category_average": None,
                "summary": "Price information not available for this product. Add a price to get value analysis!",
                "comparison_percent": None
            }

        # Get category benchmark
        category_key = product.category.lower() if product.category else "default"
        benchmark = self.CATEGORY_BENCHMARKS.get(category_key, self.CATEGORY_BENCHMARKS["default"])

        # Use unit_price (per serving) if available, otherwise use total price
        unit_price = product.unit_price if product.unit_price else product.price

        # Determine rating
        is_good_deal, rating = self._determine_rating(unit_price, benchmark)

        # Generate AI summary
        summary = await self._generate_summary(product, unit_price, benchmark, rating)

        return {
            "is_good_deal": is_good_deal,
            "rating": rating,
            "unit_price": unit_price,
            "category_average": benchmark["avg"],
            "summary": summary,
            "comparison_percent": ((unit_price - benchmark["avg"]) / benchmark["avg"]) * 100
        }

    def _determine_rating(self, unit_price: float, benchmark: Dict) -> tuple[bool, str]:
        """Determine price rating based on benchmark."""
        is_good_deal = unit_price <= benchmark["avg"]

        if unit_price <= benchmark["low"]:
            rating = "Excellent Deal"
        elif unit_price <= benchmark["avg"]:
            rating = "Good Price"
        elif unit_price <= benchmark["high"]:
            rating = "Fair Price"
        else:
            rating = "Expensive"

        return is_good_deal, rating

    async def _generate_summary(
        self,
        product: Product,
        unit_price: float,
        benchmark: Dict,
        rating: str
    ) -> str:
        """Generate AI-powered price summary."""
        servings = product.nutrition.get('servings_per_container') if product.nutrition else None

        prompt = f"""You are a price analysis expert and helpful AI companion. Analyze the pricing for this product in a friendly, conversational way:

Product: {product.name}
Category: {product.category}
Total Package Price: ${product.price:.2f}
{f'Servings Per Container: {servings}' if servings else ''}
Price Per Serving: ${unit_price:.2f}

Based on the category average (${benchmark['avg']:.2f} per serving), this product is rated as: {rating}

Provide a brief 2-3 sentence friendly summary explaining whether this is a good value PER SERVING. Consider:
- Per-serving price compared to category average
- Total value for the package
- Overall value for money

Be conversational and helpful! Focus on the per-serving value."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()

        except Exception as e:
            print(f"Price analysis failed: {e}")
            return self._generate_fallback_summary(product, unit_price, benchmark, rating)

    def _generate_fallback_summary(
        self,
        product: Product,
        unit_price: float,
        benchmark: Dict,
        rating: str
    ) -> str:
        """Generate simple summary without AI."""
        comparison_percent = ((unit_price - benchmark["avg"]) / benchmark["avg"]) * 100
        servings = product.nutrition.get('servings_per_container') if product.nutrition else None

        if rating == "Excellent Deal":
            return f"Great news! At ${unit_price:.2f} per serving, this {product.name} is an excellent deal - {abs(comparison_percent):.0f}% below average. Fantastic value for money!"
        elif rating == "Good Price":
            return f"At ${unit_price:.2f} per serving (${product.price:.2f} total{f' for {servings} servings' if servings else ''}), this {product.name} offers good value for your money!"
        elif rating == "Fair Price":
            return f"This product costs ${unit_price:.2f} per serving, which is {abs(comparison_percent):.0f}% {'above' if comparison_percent > 0 else 'below'} average. Fair price, though you might find better deals."
        else:
            return f"At ${unit_price:.2f} per serving, this {product.name} is priced {comparison_percent:.0f}% above average. Total cost: ${product.price:.2f}. Consider if it justifies the premium."
