from typing import Dict
from models.product import Product
from services.llm_service import LLMService


class PriceEvaluatorAgent:
    """Agent responsible for evaluating product pricing"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        
        # Category average prices (per unit) - these would ideally come from a database
        self.category_benchmarks = {
            "snacks": {"low": 0.10, "avg": 0.20, "high": 0.35},
            "beverages": {"low": 0.05, "avg": 0.12, "high": 0.25},
            "dairy": {"low": 0.15, "avg": 0.30, "high": 0.50},
            "cereals": {"low": 0.12, "avg": 0.25, "high": 0.40},
            "frozen": {"low": 0.20, "avg": 0.35, "high": 0.55},
            "default": {"low": 0.10, "avg": 0.25, "high": 0.45},
        }
    
    async def evaluate(self, product: Product) -> Dict:
        """
        Evaluate if product price is good
        
        Args:
            product: Product to evaluate
            
        Returns:
            Dictionary with price analysis
        """
        # Get category benchmark
        category_key = product.category.lower() if product.category else "default"
        benchmark = self.category_benchmarks.get(category_key, self.category_benchmarks["default"])
        
        # Calculate price per unit if available
        unit_price = product.unit_price if product.unit_price else product.price
        
        # Determine if it's a good deal
        is_good_deal = unit_price <= benchmark["avg"]
        
        # Determine rating
        if unit_price <= benchmark["low"]:
            rating = "Excellent Deal"
        elif unit_price <= benchmark["avg"]:
            rating = "Good Price"
        elif unit_price <= benchmark["high"]:
            rating = "Fair Price"
        else:
            rating = "Expensive"
        
        # Generate summary (try LLM first, fallback to template)
        try:
            # Use LLM for detailed analysis
            prompt = f"""Analyze the pricing for this product:
Product: {product.name}
Brand: {product.brand}
Category: {product.category}
Price: ${product.price:.2f}
{f'Size: {product.size}' if product.size else ''}
{f'Unit Price: ${unit_price:.2f}' if unit_price else ''}

Based on the category average (${benchmark['avg']:.2f} per unit), this product is rated as: {rating}

Provide a brief 2-3 sentence summary explaining whether this is a good value. Consider:
- Price compared to category average
- Brand positioning (premium vs budget)
- Value for money
"""

            summary = await self.llm.generate(prompt, max_tokens=150)

            # If summary contains an error, use fallback
            if "Error:" in summary or "Unable to generate" in summary:
                summary = self._generate_fallback_summary(product, unit_price, benchmark, rating)
        except Exception as e:
            print(f"LLM analysis failed, using fallback: {e}")
            summary = self._generate_fallback_summary(product, unit_price, benchmark, rating)

        return {
            "is_good_deal": is_good_deal,
            "rating": rating,
            "unit_price": unit_price,
            "category_average": benchmark["avg"],
            "summary": summary.strip(),
            "comparison_percent": ((unit_price - benchmark["avg"]) / benchmark["avg"]) * 100
        }

    def _generate_fallback_summary(self, product: Product, unit_price: float, benchmark: Dict, rating: str) -> str:
        """Generate a simple summary without LLM"""
        comparison_percent = ((unit_price - benchmark["avg"]) / benchmark["avg"]) * 100

        if rating == "Excellent Deal":
            return f"This {product.name} is an excellent deal, priced {abs(comparison_percent):.0f}% below the category average. This is a great value for money in the {product.category} category."
        elif rating == "Good Price":
            return f"The {product.name} is reasonably priced at ${product.price:.2f}, offering good value compared to similar {product.category} products. This is a solid choice for budget-conscious shoppers."
        elif rating == "Fair Price":
            return f"This product is priced at ${product.price:.2f}, which is {abs(comparison_percent):.0f}% {'above' if comparison_percent > 0 else 'below'} average for {product.category}. It's a fair price, though you might find better deals."
        else:  # Expensive
            return f"At ${product.price:.2f}, this {product.name} is priced {comparison_percent:.0f}% above the category average. Consider if the brand premium justifies the higher cost, or look for alternatives."