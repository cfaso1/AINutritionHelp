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

    def __init__(self, model_name: str = "gemini-2.0-flash"):
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
                "comparison_percent": None,
                "value_metrics": {}
            }

        # Calculate comprehensive value metrics
        value_metrics = self._calculate_value_metrics(product)

        # Get category benchmark
        category_key = product.category.lower() if product.category else "default"
        benchmark = self.CATEGORY_BENCHMARKS.get(category_key, self.CATEGORY_BENCHMARKS["default"])

        # Use unit_price (per serving) if available, otherwise use total price
        unit_price = product.unit_price if product.unit_price else product.price

        # Determine rating based on multiple factors
        is_good_deal, rating = self._determine_rating_advanced(
            unit_price, benchmark, value_metrics
        )

        # Generate AI summary
        summary = await self._generate_summary(
            product, unit_price, benchmark, rating, value_metrics
        )

        return {
            "is_good_deal": is_good_deal,
            "rating": rating,
            "unit_price": unit_price,
            "category_average": benchmark["avg"],
            "summary": summary,
            "comparison_percent": ((unit_price - benchmark["avg"]) / benchmark["avg"]) * 100,
            "value_metrics": value_metrics
        }

    def _calculate_value_metrics(self, product: Product) -> Dict:
        """
        Calculate comprehensive value metrics for price evaluation.

        Returns:
            Dictionary with various value-per-dollar metrics
        """
        if not product.nutrition or not product.price:
            return {}

        nutrition = product.nutrition
        price = product.price

        # Get nutritional values
        calories = nutrition.get('calories', 0) or 0
        protein = nutrition.get('protein', 0) or 0
        fiber = nutrition.get('dietary_fiber', 0) or 0
        serving_size_str = nutrition.get('serving_size', '100g')
        servings = nutrition.get('servings_per_container', 1) or 1

        # Extract serving size in grams
        import re
        serving_grams = 100  # default
        match = re.search(r'(\d+\.?\d*)g', str(serving_size_str))
        if match:
            serving_grams = float(match.group(1))

        # Calculate total nutrition in package
        total_calories = calories * servings
        total_protein = protein * servings
        total_fiber = fiber * servings
        total_grams = serving_grams * servings

        metrics = {}

        # Price per calorie (cents per calorie)
        if total_calories > 0:
            metrics['price_per_calorie'] = (price / total_calories) * 100
            metrics['calories_per_dollar'] = total_calories / price

        # Price per 100g (standardized)
        if total_grams > 0:
            metrics['price_per_100g'] = (price / total_grams) * 100
            metrics['grams_per_dollar'] = total_grams / price

        # Protein value
        if total_protein > 0:
            metrics['price_per_gram_protein'] = price / total_protein
            metrics['protein_per_dollar'] = total_protein / price

        # Fiber value
        if total_fiber > 0:
            metrics['price_per_gram_fiber'] = price / total_fiber
            metrics['fiber_per_dollar'] = total_fiber / price

        # Overall nutritional value score (higher is better)
        # Based on calories for energy, protein for nutrition, fiber for health
        if price > 0:
            nutrition_score = (
                (total_calories / 100) +  # Energy value
                (total_protein * 4) +      # Protein value (4x weight)
                (total_fiber * 3)          # Fiber value (3x weight)
            ) / price
            metrics['nutrition_value_score'] = nutrition_score

        # Add total package info
        metrics['total_calories'] = total_calories
        metrics['total_protein'] = total_protein
        metrics['total_fiber'] = total_fiber
        metrics['total_grams'] = total_grams

        return metrics

    def _determine_rating_advanced(
        self, unit_price: float, benchmark: Dict, value_metrics: Dict
    ) -> tuple[bool, str]:
        """
        Determine price rating based on multiple value factors.

        Considers not just per-serving price, but also nutritional value.
        """
        # Start with basic per-serving rating
        is_good_deal = unit_price <= benchmark["avg"]

        if unit_price <= benchmark["low"]:
            base_rating = "Excellent Deal"
        elif unit_price <= benchmark["avg"]:
            base_rating = "Good Price"
        elif unit_price <= benchmark["high"]:
            base_rating = "Fair Price"
        else:
            base_rating = "Expensive"

        # Adjust rating based on nutritional value
        if value_metrics:
            # If product provides exceptional nutritional value, upgrade rating
            nutrition_score = value_metrics.get('nutrition_value_score', 0)
            calories_per_dollar = value_metrics.get('calories_per_dollar', 0)
            protein_per_dollar = value_metrics.get('protein_per_dollar', 0)

            # High nutrition score can improve perception
            if nutrition_score > 50 or protein_per_dollar > 20:
                # Good nutritional value - might justify higher price
                if base_rating == "Expensive":
                    base_rating = "Fair Price (High Nutrition)"
                elif base_rating == "Fair Price":
                    is_good_deal = True

            # Very poor value can downgrade rating
            if calories_per_dollar < 50 and protein_per_dollar < 5:
                if base_rating == "Good Price":
                    base_rating = "Fair Price"

        return is_good_deal, base_rating

    def _determine_rating(self, unit_price: float, benchmark: Dict) -> tuple[bool, str]:
        """Determine price rating based on benchmark (legacy method)."""
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
        rating: str,
        value_metrics: Dict
    ) -> str:
        """Generate AI-powered price summary."""
        servings = product.nutrition.get('servings_per_container') if product.nutrition else None

        # Build value metrics section for prompt
        metrics_text = ""
        if value_metrics:
            metrics_text = "\n**Value Analysis:**"

            if 'price_per_calorie' in value_metrics:
                metrics_text += f"\n- Price per calorie: {value_metrics['price_per_calorie']:.2f}¢/cal"
                metrics_text += f"\n- Calories per dollar: {value_metrics['calories_per_dollar']:.0f} cal/$"

            if 'price_per_100g' in value_metrics:
                metrics_text += f"\n- Price per 100g: ${value_metrics['price_per_100g']:.2f}"
                metrics_text += f"\n- Total weight: {value_metrics['total_grams']:.0f}g"

            if 'protein_per_dollar' in value_metrics:
                metrics_text += f"\n- Protein per dollar: {value_metrics['protein_per_dollar']:.1f}g/$"

            if 'fiber_per_dollar' in value_metrics:
                metrics_text += f"\n- Fiber per dollar: {value_metrics['fiber_per_dollar']:.1f}g/$"

            if 'nutrition_value_score' in value_metrics:
                metrics_text += f"\n- Nutrition value score: {value_metrics['nutrition_value_score']:.1f}"

        prompt = f"""You are a price analysis expert and helpful AI companion. Analyze the pricing for this product in a friendly, conversational way:

Product: {product.name}
Category: {product.category}
Total Package Price: ${product.price:.2f}
{f'Servings Per Container: {servings}' if servings else ''}
Price Per Serving: ${unit_price:.2f}
{metrics_text}

Based on the category average (${benchmark['avg']:.2f} per serving), this product is rated as: {rating}

Provide a brief 2-3 sentence friendly summary explaining whether this is a good value. Consider MULTIPLE VALUE FACTORS:
- Price per serving vs category average
- Price per calorie (energy value)
- Price per gram (amount of food)
- Nutritional value per dollar (protein, fiber)
- Overall package value

Be conversational and helpful! Highlight the BEST value aspect (e.g., "great calorie value" or "excellent protein per dollar")."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()

        except Exception as e:
            print(f"Price analysis failed: {e}")
            return self._generate_fallback_summary(product, unit_price, benchmark, rating, value_metrics)

    def _generate_fallback_summary(
        self,
        product: Product,
        unit_price: float,
        benchmark: Dict,
        rating: str,
        value_metrics: Dict
    ) -> str:
        """Generate simple summary without AI."""
        comparison_percent = ((unit_price - benchmark["avg"]) / benchmark["avg"]) * 100
        servings = product.nutrition.get('servings_per_container') if product.nutrition else None

        # Find best value aspect to highlight
        best_value = ""
        if value_metrics:
            calories_per_dollar = value_metrics.get('calories_per_dollar', 0)
            protein_per_dollar = value_metrics.get('protein_per_dollar', 0)

            if protein_per_dollar > 20:
                best_value = f" Excellent protein value at {protein_per_dollar:.0f}g per dollar!"
            elif calories_per_dollar > 300:
                best_value = f" Great energy value with {calories_per_dollar:.0f} calories per dollar!"
            elif value_metrics.get('nutrition_value_score', 0) > 50:
                best_value = " Strong overall nutritional value!"

        if rating == "Excellent Deal":
            return f"Great news! At ${unit_price:.2f} per serving, this {product.name} is an excellent deal - {abs(comparison_percent):.0f}% below average.{best_value or ' Fantastic value for money!'}"
        elif rating == "Good Price":
            return f"At ${unit_price:.2f} per serving (${product.price:.2f} total{f' for {servings} servings' if servings else ''}), this {product.name} offers good value for your money!{best_value}"
        elif "High Nutrition" in rating:
            return f"While priced above average at ${unit_price:.2f} per serving, the strong nutritional value makes this a reasonable choice.{best_value}"
        elif rating == "Fair Price":
            return f"This product costs ${unit_price:.2f} per serving, which is {abs(comparison_percent):.0f}% {'above' if comparison_percent > 0 else 'below'} average.{best_value or ' Fair price, though you might find better deals.'}"
        else:
            return f"At ${unit_price:.2f} per serving, this {product.name} is priced {comparison_percent:.0f}% above average. Total cost: ${product.price:.2f}.{best_value or ' Consider if it justifies the premium.'}"
