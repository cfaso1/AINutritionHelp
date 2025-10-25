from typing import Dict, List
from models.product import Product
from models.user_profile import UserProfile
from services.llm_service import LLMService


class HealthEvaluatorAgent:
    """Agent responsible for evaluating product health alignment"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def evaluate(self, product: Product, user_profile: UserProfile) -> Dict:
        """
        Evaluate how well product aligns with health goals
        
        Args:
            product: Product to evaluate
            user_profile: User's health goals and preferences
            
        Returns:
            Dictionary with health analysis
        """
        if not product.has_nutrition_info():
            return self._no_nutrition_response()
        
        # Build nutrition summary
        nutrition_summary = self._build_nutrition_summary(product)
        
        # Build analysis prompt
        prompt = f"""You are a nutrition expert. Analyze this product for someone with these health goals: {user_profile.health_goals}

Product: {product.name}
Brand: {product.brand}
Category: {product.category}

Nutritional Information (per serving):
{nutrition_summary}

{f'Ingredients: {product.ingredients[:200]}...' if product.ingredients else 'Ingredients: Not available'}

Task: Provide a structured analysis with:
1. A health score from 0-100 (how well it aligns with their goals)
2. A brief 2-3 sentence summary
3. Top 3 pros (nutritional positives)
4. Top 3 cons (nutritional concerns)

Format your response EXACTLY like this:
SCORE: [number]
SUMMARY: [your summary]
PROS: [pro1] | [pro2] | [pro3]
CONS: [con1] | [con2] | [con3]
"""
        
        response = await self.llm.generate(prompt, max_tokens=400)
        
        # Parse response
        return self._parse_health_response(response)
    
    def _build_nutrition_summary(self, product: Product) -> str:
        """Build nutrition summary string"""
        if not product.nutrition:
            return "No nutrition information available"
        
        lines = []
        nutrition_display = {
            "calories": "Calories",
            "protein": "Protein (g)",
            "carbohydrates": "Carbohydrates (g)",
            "sugar": "Sugar (g)",
            "fat": "Total Fat (g)",
            "saturated_fat": "Saturated Fat (g)",
            "sodium": "Sodium (mg)",
            "fiber": "Fiber (g)"
        }
        
        for key, label in nutrition_display.items():
            value = product.nutrition.get(key, 0)
            if value > 0:
                lines.append(f"- {label}: {value}")
        
        return "\n".join(lines)
    
    def _parse_health_response(self, response: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            lines = response.strip().split("\n")
            result = {
                "score": 50,
                "summary": "",
                "pros": [],
                "cons": []
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith("SCORE:"):
                    try:
                        result["score"] = int(line.split(":")[1].strip())
                    except:
                        pass
                elif line.startswith("SUMMARY:"):
                    result["summary"] = line.split(":", 1)[1].strip()
                elif line.startswith("PROS:"):
                    pros_text = line.split(":", 1)[1].strip()
                    result["pros"] = [p.strip() for p in pros_text.split("|") if p.strip()]
                elif line.startswith("CONS:"):
                    cons_text = line.split(":", 1)[1].strip()
                    result["cons"] = [c.strip() for c in cons_text.split("|") if c.strip()]
            
            # Ensure we have at least some default values
            if not result["summary"]:
                result["summary"] = "Unable to generate detailed analysis."
            if not result["pros"]:
                result["pros"] = ["Analysis incomplete"]
            if not result["cons"]:
                result["cons"] = ["Analysis incomplete"]
            
            return result
        except Exception as e:
            return {
                "score": 50,
                "summary": "Error parsing health analysis.",
                "pros": ["Unable to determine"],
                "cons": ["Unable to determine"]
            }
    
    def _no_nutrition_response(self) -> Dict:
        """Return response when no nutrition info available"""
        return {
            "score": 0,
            "summary": "Cannot evaluate health alignment - no nutrition information available for this product.",
            "pros": ["N/A"],
            "cons": ["Missing nutrition data"]
        }