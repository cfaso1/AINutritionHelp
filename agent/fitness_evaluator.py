"""
Fitness Evaluator - Analyzes products for fitness and workout alignment.
"""

import os
from typing import Dict
from google import genai
from dotenv import load_dotenv

from agent.models import Product, UserProfile
from agent.utils.data_parser import calculate_macros, extract_nutrition_value

load_dotenv()


class FitnessEvaluator:
    """
    Evaluates products based on fitness goals and activity needs.

    Analyzes macronutrient ratios and provides fitness scores, timing
    recommendations, and workout-related guidance.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Fitness Evaluator with AI model."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def evaluate(self, product: Product, user_profile: UserProfile) -> Dict:
        """
        Evaluate product fitness alignment.

        Args:
            product: Product to evaluate
            user_profile: User's fitness goals

        Returns:
            Fitness analysis with score, summary, best_for, and recommendation
        """
        if not product.has_nutrition_info():
            return self._no_nutrition_response()

        # Calculate macronutrient ratios
        protein = extract_nutrition_value(product.nutrition, 'protein')
        carbs = extract_nutrition_value(product.nutrition, 'carbohydrates')
        fat = extract_nutrition_value(product.nutrition, 'fat')
        macros = calculate_macros(protein, carbs, fat)

        prompt = f"""You are a fitness nutrition expert and AI companion. Analyze this product for someone with these fitness goals: {user_profile.fitness_goals}

Product: {product.name}
Category: {product.category}

Nutritional Profile:
- Calories: {extract_nutrition_value(product.nutrition, 'calories')}
- Protein: {protein}g ({macros['protein_percent']:.1f}%)
- Carbohydrates: {carbs}g ({macros['carb_percent']:.1f}%)
- Fat: {fat}g ({macros['fat_percent']:.1f}%)
- Sugar: {extract_nutrition_value(product.nutrition, 'sugar')}g
- Fiber: {extract_nutrition_value(product.nutrition, 'fiber')}g

User's activity level: {user_profile.activity_level if user_profile.activity_level else 'Not specified'}
User's protein target: {user_profile.daily_protein_target_g}g per day
User's goal type: {user_profile.goal_type if user_profile.goal_type else 'general fitness'}

Provide a conversational, friendly fitness analysis with:
1. A fitness score from 0-100 (how well it supports their goals)
2. A brief 2-3 sentence summary in a friendly tone
3. Best timing/use case (e.g., "pre-workout", "post-workout", "daily snack")
4. A specific recommendation

Format EXACTLY like this:
SCORE: [number]
SUMMARY: [your friendly summary]
BEST_FOR: [timing/use case]
RECOMMENDATION: [your recommendation]
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            return self._parse_response(response.text)

        except Exception as e:
            print(f"Fitness evaluation failed: {e}")
            return self._generate_fallback_analysis(product, user_profile, macros)

    def _parse_response(self, response: str) -> Dict:
        """Parse AI response into structured format."""
        try:
            lines = [line.strip() for line in response.strip().split("\n") if line.strip()]
            result = {
                "score": 50,
                "summary": "",
                "best_for": "",
                "recommendation": ""
            }

            for line in lines:
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

            # Ensure defaults
            if not result["summary"]:
                result["summary"] = "Unable to generate detailed analysis."
            if not result["best_for"]:
                result["best_for"] = "General consumption"
            if not result["recommendation"]:
                result["recommendation"] = "Consume in moderation"

            return result

        except Exception as e:
            print(f"Error parsing fitness response: {e}")
            return {
                "score": 50,
                "summary": "Error parsing fitness analysis.",
                "best_for": "Unable to determine",
                "recommendation": "Consult with a nutritionist"
            }

    def _generate_fallback_analysis(
        self,
        product: Product,
        user_profile: UserProfile,
        macros: Dict
    ) -> Dict:
        """Generate basic fitness analysis without AI."""
        if not product.nutrition:
            return self._no_nutrition_response()

        nutrition = product.nutrition
        protein = extract_nutrition_value(nutrition, 'protein')
        carbs = extract_nutrition_value(nutrition, 'carbohydrates')
        fat = extract_nutrition_value(nutrition, 'fat')
        calories = extract_nutrition_value(nutrition, 'calories')
        sugar = extract_nutrition_value(nutrition, 'sugar')

        score = 50
        best_for = "general snack"
        recommendation = ""

        # High protein products
        if protein >= 20:
            score += 20
            best_for = "post-workout recovery or muscle building"
            recommendation = "Excellent protein source for muscle recovery and growth!"
        elif protein >= 10:
            score += 10
            best_for = "protein supplement"
            recommendation = "Good protein content to support your fitness goals."

        # Sugar analysis
        if sugar <= 5:
            score += 10
        elif sugar > 15:
            score -= 10
            recommendation = "High sugar content - best consumed before/during intense workouts only."

        # Protein percentage
        if macros['protein_percent'] >= 30:
            score += 10

        # Pre-workout (high carbs, low fat)
        if carbs >= 30 and fat < 5:
            best_for = "pre-workout energy"
            score += 5

        # Post-workout (protein + carbs)
        if protein >= 15 and 20 <= carbs <= 40:
            best_for = "post-workout recovery"
            score += 10

        score = max(0, min(100, score))

        summary = f"This {product.name} provides {calories} calories with {protein}g protein ({macros['protein_percent']:.0f}%), {carbs}g carbs, and {fat}g fat. "
        summary += "Perfect for your fitness goals!" if score >= 70 else \
                   "Can fit into your fitness nutrition plan with mindful consumption." if score >= 50 else \
                   "Consider alternatives more aligned with your fitness nutrition needs."

        if not recommendation:
            recommendation = "Great choice for active individuals! Include this as part of your balanced fitness nutrition plan." if score >= 70 else \
                           "Better options available for your fitness goals. Use sparingly."

        return {
            "score": score,
            "summary": summary,
            "best_for": best_for,
            "recommendation": recommendation
        }

    def _no_nutrition_response(self) -> Dict:
        """Response when nutrition info unavailable."""
        return {
            "score": 0,
            "summary": "I can't evaluate fitness alignment without nutrition information for this product.",
            "best_for": "N/A",
            "recommendation": "Find a product with nutrition information"
        }
