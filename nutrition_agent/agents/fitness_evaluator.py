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
        
        response = await self.llm.generate(prompt, max_tokens=400)
        
        # Parse response
        return self._parse_fitness_response(response)
    
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
    
    def _no_nutrition_response(self) -> Dict:
        """Return response when no nutrition info available"""
        return {
            "score": 0,
            "summary": "Cannot evaluate fitness alignment - no nutrition information available for this product.",
            "best_for": "N/A",
            "recommendation": "Find a product with nutrition information"
        }