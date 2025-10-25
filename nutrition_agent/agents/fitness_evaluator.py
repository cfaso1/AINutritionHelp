from typing import Dict
from models.product import Product
from models.user_profile import UserProfile
from services.llm_service import LLMService


class FitnessEvaluatorAgent:
    """Agent responsible for evaluating product fitness alignment"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def evaluate(self, product: Product, user_profile: UserProfile) -> Dict:
        """
        Evaluate how well product aligns with fitness goals
        
        Args:
            product: Product to evaluate
            user_profile: User's fitness goals
            
        Returns:
            Dictionary with fitness analysis
        """
        if not product.has_nutrition_info():
            return self._no_nutrition_response()
        
        # Calculate macronutrient ratios
        macros = self._calculate_macros(product)
        
        # Build analysis prompt
        prompt = f"""You are a fitness nutrition expert. Analyze this product for someone with these fitness goals: {user_profile.fitness_goals}

Product: {product.name}
Category: {product.category}

Nutritional Profile:
- Calories: {product.get_nutrition_value('calories')}
- Protein: {product.get_nutrition_value('protein')}g ({macros['protein_percent']:.1f}%)
- Carbohydrates: {product.get_nutrition_value('carbohydrates')}g ({macros['carb_percent']:.1f}%)
- Fat: {product.get_nutrition_value('fat')}g ({macros['fat_percent']:.1f}%)
- Sugar: {product.get_nutrition_value('sugar')}g
- Fiber: {product.get_nutrition_value('fiber')}g

Task: Provide a structured analysis with:
1. A fitness score from 0-100 (how well it supports their goals)
2. A brief 2-3 sentence summary
3. Best timing/use case (e.g., "pre-workout", "post-workout", "daily snack")
4. A specific recommendation

Format your response EXACTLY like this:
SCORE: [number]
SUMMARY: [your summary]
BEST_FOR: [timing/use case]
RECOMMENDATION: [your recommendation]
"""
        
        try:
            response = await self.llm.generate(prompt, max_tokens=400)

            # Check if response contains error
            if "Error:" in response or "Unable to generate" in response:
                print(f"LLM fitness analysis failed, using fallback")
                return self._generate_fallback_analysis(product, user_profile, macros)

            # Parse response
            return self._parse_fitness_response(response)
        except Exception as e:
            print(f"Fitness evaluation failed: {e}, using fallback")
            return self._generate_fallback_analysis(product, user_profile, macros)
    
    def _calculate_macros(self, product: Product) -> Dict[str, float]:
        """Calculate macronutrient percentages"""
        protein = product.get_nutrition_value('protein')
        carbs = product.get_nutrition_value('carbohydrates')
        fat = product.get_nutrition_value('fat')
        
        # Calculate calories from macros (protein: 4cal/g, carbs: 4cal/g, fat: 9cal/g)
        total_macro_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        
        if total_macro_calories == 0:
            return {
                'protein_percent': 0,
                'carb_percent': 0,
                'fat_percent': 0
            }
        
        return {
            'protein_percent': (protein * 4 / total_macro_calories) * 100,
            'carb_percent': (carbs * 4 / total_macro_calories) * 100,
            'fat_percent': (fat * 9 / total_macro_calories) * 100
        }
    
    def _parse_fitness_response(self, response: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            lines = response.strip().split("\n")
            result = {
                "score": 50,
                "summary": "",
                "best_for": "",
                "recommendation": ""
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
                elif line.startswith("BEST_FOR:"):
                    result["best_for"] = line.split(":", 1)[1].strip()
                elif line.startswith("RECOMMENDATION:"):
                    result["recommendation"] = line.split(":", 1)[1].strip()
            
            # Ensure we have at least some default values
            if not result["summary"]:
                result["summary"] = "Unable to generate detailed analysis."
            if not result["best_for"]:
                result["best_for"] = "General consumption"
            if not result["recommendation"]:
                result["recommendation"] = "Consume in moderation"
            
            return result
        except Exception as e:
            return {
                "score": 50,
                "summary": "Error parsing fitness analysis.",
                "best_for": "Unable to determine",
                "recommendation": "Consult with a nutritionist"
            }
    
    def _generate_fallback_analysis(self, product: Product, user_profile: UserProfile, macros: Dict) -> Dict:
        """Generate basic fitness analysis without LLM"""
        if not product.nutrition:
            return self._no_nutrition_response()

        nutrition = product.nutrition
        protein = nutrition.get("protein", 0)
        carbs = nutrition.get("carbohydrates", 0)
        fat = nutrition.get("fat", 0)
        calories = nutrition.get("calories", 0)
        sugar = nutrition.get("sugar", 0)

        score = 50  # Start neutral
        best_for = "general snack"
        recommendation = ""

        # High protein products
        if protein >= 20:
            score += 20
            best_for = "post-workout recovery or muscle building"
            recommendation = "Excellent protein source for muscle recovery and growth."
        elif protein >= 10:
            score += 10
            best_for = "protein supplement"
            recommendation = "Good protein content to support fitness goals."

        # Low sugar is good for fitness
        if sugar <= 5:
            score += 10
        elif sugar > 15:
            score -= 10
            recommendation = "High sugar content - consume before/during intense workouts only."

        # Evaluate protein percentage
        if macros['protein_percent'] >= 30:
            score += 10
        elif macros['protein_percent'] < 10:
            score -= 5

        # Evaluate for pre-workout (higher carbs)
        if carbs >= 30 and fat < 5:
            best_for = "pre-workout energy"
            score += 5

        # Evaluate for post-workout (protein + carbs)
        if protein >= 15 and carbs >= 20 and carbs <= 40:
            best_for = "post-workout recovery"
            score += 10

        # Clamp score
        score = max(0, min(100, score))

        summary = f"This {product.name} provides {calories} calories with {protein}g protein ({macros['protein_percent']:.0f}%), {carbs}g carbs ({macros['carb_percent']:.0f}%), and {fat}g fat ({macros['fat_percent']:.0f}%). "
        if score >= 70:
            summary += "Well-suited for fitness goals."
        elif score >= 50:
            summary += "Can fit into a fitness nutrition plan with mindful consumption."
        else:
            summary += "Consider alternatives more aligned with fitness nutrition."

        if not recommendation:
            if score >= 70:
                recommendation = "Good choice for active individuals. Consume as part of a balanced fitness nutrition plan."
            else:
                recommendation = "Better options available for fitness goals. Use sparingly."

        return {
            "score": score,
            "summary": summary,
            "best_for": best_for,
            "recommendation": recommendation
        }

    def _no_nutrition_response(self) -> Dict:
        """Return response when no nutrition info available"""
        return {
            "score": 0,
            "summary": "Cannot evaluate fitness alignment - no nutrition information available for this product.",
            "best_for": "N/A",
            "recommendation": "Find a product with nutrition information"
        }

import asyncio

_fitness_agent_instance = None

def get_fitness_agent():
    """Get or create singleton instance of FitnessEvaluatorAgent"""
    global _fitness_agent_instance
    if _fitness_agent_instance is None:
        _fitness_agent_instance = FitnessEvaluatorAgent()
    return _fitness_agent_instance


def evaluate_fitness(
    product_data: dict,
    fitness_goals: list
) -> dict:
    """
    Evaluate a product against user's fitness goals.
    
    This tool analyzes macronutrient ratios and nutritional content to determine
    how well a product supports specific fitness objectives like muscle building,
    weight loss, endurance training, etc.
    
    Args:
        product_data: Dictionary containing product information (from scan_barcode)
        fitness_goals: List of fitness goals (e.g., ["muscle building", "weight loss"])
        
    Returns:
        Dictionary with fitness score (0-100), macro analysis, timing recommendations, and insights
    """
    from models.product import Product
    
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
    
    agent = get_fitness_agent()
    
    # Run the async function synchronously
    try:
        result = asyncio.run(agent.evaluate(product, fitness_goals))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(lambda: asyncio.run(agent.evaluate(product, fitness_goals))).result()
        else:
            result = asyncio.run(agent.evaluate(product, fitness_goals))
    
    return result


__all__ = ['evaluate_fitness', 'FitnessEvaluatorAgent', 'get_fitness_agent']