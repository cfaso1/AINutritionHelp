from typing import Dict, List
from models.product import Product
from models.user_profile import UserProfile
from services.llm_service import LLMService
import asyncio
from typing import Optional

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
        
        try:
            response = await self.llm.generate(prompt, max_tokens=400)

            # Check if response contains error
            if "Error:" in response or "Unable to generate" in response:
                print(f"LLM health analysis failed, using fallback")
                return self._generate_fallback_analysis(product, user_profile)

            # Parse response
            return self._parse_health_response(response)
        except Exception as e:
            print(f"Health evaluation failed: {e}, using fallback")
            return self._generate_fallback_analysis(product, user_profile)
    
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
    
    def _generate_fallback_analysis(self, product: Product, user_profile: UserProfile) -> Dict:
        """Generate basic health analysis without LLM"""
        if not product.nutrition:
            return self._no_nutrition_response()

        nutrition = product.nutrition
        score = 50  # Start neutral
        pros = []
        cons = []

        # Analyze protein
        protein = nutrition.get("protein", 0)
        if protein >= 15:
            pros.append(f"High protein content ({protein}g)")
            score += 10
        elif protein >= 10:
            pros.append(f"Good protein content ({protein}g)")
            score += 5

        # Analyze sugar
        sugar = nutrition.get("sugar", 0)
        if sugar <= 5:
            pros.append(f"Low sugar ({sugar}g)")
            score += 10
        elif sugar > 20:
            cons.append(f"High sugar content ({sugar}g)")
            score -= 10

        # Analyze fiber
        fiber = nutrition.get("fiber", 0)
        if fiber >= 5:
            pros.append(f"Good fiber content ({fiber}g)")
            score += 10
        elif fiber >= 3:
            pros.append(f"Contains fiber ({fiber}g)")
            score += 5

        # Analyze sodium
        sodium = nutrition.get("sodium", 0)
        if sodium > 400:
            cons.append(f"High sodium ({sodium}mg)")
            score -= 10
        elif sodium > 200:
            cons.append(f"Moderate sodium ({sodium}mg)")
            score -= 5

        # Analyze calories
        calories = nutrition.get("calories", 0)
        if calories > 300:
            cons.append(f"High calorie content ({calories} cal)")
            score -= 5

        # Ensure we have at least something
        if not pros:
            pros.append("Contains essential nutrients")
        if not cons:
            cons.append("Review serving size for daily intake")

        # Clamp score
        score = max(0, min(100, score))

        summary = f"This {product.name} has {calories} calories per serving with {protein}g protein. "
        if score >= 70:
            summary += "Overall, it appears to be a nutritious choice."
        elif score >= 50:
            summary += "It has some nutritional benefits but should be consumed mindfully."
        else:
            summary += "Consider healthier alternatives or consume in moderation."

        return {
            "score": score,
            "summary": summary,
            "pros": pros[:3],
            "cons": cons[:3]
        }

    def _no_nutrition_response(self) -> Dict:
        """Return response when no nutrition info available"""
        return {
            "score": 0,
            "summary": "Cannot evaluate health alignment - no nutrition information available for this product.",
            "pros": ["N/A"],
            "cons": ["Missing nutrition data"]
        }

        _health_agent_instance = None

def get_health_agent():
    """Get or create singleton instance of HealthEvaluatorAgent"""
    global _health_agent_instance
    if _health_agent_instance is None:
        _health_agent_instance = HealthEvaluatorAgent()
    return _health_agent_instance

def evaluate_health(product_data: dict, health_goals: list, dietary_restrictions: Optional[list] = None) -> dict:
    """Evaluate a product against user's health goals."""
    product = Product(
        barcode=product_data.get("barcode", ""),
        name=product_data.get("name", ""),
        brand=product_data.get("brand", ""),
        category=product_data.get("category", ""),
        price=product_data.get("price", 0),
        size=product_data.get("size"),
        unit_price=product_data.get("unit_price"),
        nutrition=product_data.get("nutrition"),
        ingredients=product_data.get("ingredients")
    )
    
    agent = get_health_agent()
    try:
        result = asyncio.run(agent.evaluate(product, health_goals, dietary_restrictions or []))
    except Exception as e:
        result = {"success": False, "error": str(e)}
    return result

__all__ = ['evaluate_health', 'HealthEvaluatorAgent', 'get_health_agent']

  