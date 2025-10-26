"""
Health Evaluator - Analyzes products for health and wellness alignment.
"""

import os
from typing import Dict
from google import genai
from dotenv import load_dotenv

from agent.models import Product, UserProfile
from agent.utils.data_parser import extract_nutrition_value

load_dotenv()


class HealthEvaluator:
    """
    Evaluates products based on health goals and dietary needs.

    Analyzes nutritional content and provides health scores, pros/cons,
    and personalized recommendations.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Health Evaluator with AI model."""
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = model_name

    async def evaluate(self, product: Product, user_profile: UserProfile) -> Dict:
        """
        Evaluate product health alignment.

        Args:
            product: Product to evaluate
            user_profile: User's health goals and preferences

        Returns:
            Health analysis with score, summary, pros, and cons
        """
        if not product.has_nutrition_info():
            return self._no_nutrition_response()

        nutrition_summary = self._build_nutrition_summary(product)

        prompt = f"""You are a nutrition and health expert AI companion. Analyze this product for someone with these health goals: {user_profile.health_goals}

Product: {product.name}
Brand: {product.brand}
Category: {product.category}

Nutritional Information (per serving):
{nutrition_summary}

{f'Ingredients: {product.ingredients[:200]}...' if product.ingredients else 'Ingredients: Not available'}

User's dietary restrictions: {user_profile.dietary_restrictions if user_profile.dietary_restrictions else 'None'}
User's diet type: {user_profile.diet_type if user_profile.diet_type else 'Standard'}
User's daily calorie target: {user_profile.daily_calorie_target if user_profile.daily_calorie_target else 'Not specified'}

Provide a conversational, friendly health analysis with:
1. A health score from 0-100 (how well it aligns with their goals)
2. A brief 2-3 sentence summary in a friendly tone
3. Top 3 pros (nutritional positives)
4. Top 3 cons (nutritional concerns)

Format EXACTLY like this:
SCORE: [number]
SUMMARY: [your friendly summary]
PROS: [pro1] | [pro2] | [pro3]
CONS: [con1] | [con2] | [con3]
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            return self._parse_response(response.text)

        except Exception as e:
            print(f"Health evaluation failed: {e}")
            return self._generate_fallback_analysis(product, user_profile)

    def _build_nutrition_summary(self, product: Product) -> str:
        """Build formatted nutrition summary."""
        if not product.nutrition:
            return "No nutrition information available"

        lines = []
        nutrition_labels = {
            "calories": "Calories",
            "protein": "Protein (g)",
            "carbohydrates": "Carbohydrates (g)",
            "sugar": "Sugar (g)",
            "fat": "Total Fat (g)",
            "saturated_fat": "Saturated Fat (g)",
            "sodium": "Sodium (mg)",
            "fiber": "Fiber (g)"
        }

        for key, label in nutrition_labels.items():
            value = product.nutrition.get(key, 0)
            if value > 0:
                lines.append(f"- {label}: {value}")

        return "\n".join(lines)

    def _parse_response(self, response: str) -> Dict:
        """Parse AI response into structured format."""
        try:
            lines = [line.strip() for line in response.strip().split("\n") if line.strip()]
            result = {
                "score": 50,
                "summary": "",
                "pros": [],
                "cons": []
            }

            for line in lines:
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

            # Ensure defaults
            if not result["summary"]:
                result["summary"] = "Unable to generate detailed analysis."
            if not result["pros"]:
                result["pros"] = ["Analysis incomplete"]
            if not result["cons"]:
                result["cons"] = ["Analysis incomplete"]

            return result

        except Exception as e:
            print(f"Error parsing health response: {e}")
            return {
                "score": 50,
                "summary": "Error parsing analysis.",
                "pros": ["Unable to determine"],
                "cons": ["Unable to determine"]
            }

    def _generate_fallback_analysis(self, product: Product, user_profile: UserProfile) -> Dict:
        """Generate basic health analysis without AI."""
        if not product.nutrition:
            return self._no_nutrition_response()

        nutrition = product.nutrition
        score = 50
        pros = []
        cons = []

        # Analyze protein
        protein = extract_nutrition_value(nutrition, 'protein')
        if protein >= 15:
            pros.append(f"High protein content ({protein}g)")
            score += 10
        elif protein >= 10:
            pros.append(f"Good protein content ({protein}g)")
            score += 5

        # Analyze sugar
        sugar = extract_nutrition_value(nutrition, 'sugar')
        if sugar <= 5:
            pros.append(f"Low sugar ({sugar}g)")
            score += 10
        elif sugar > 20:
            cons.append(f"High sugar content ({sugar}g)")
            score -= 10

        # Analyze fiber
        fiber = extract_nutrition_value(nutrition, 'fiber')
        if fiber >= 5:
            pros.append(f"Good fiber content ({fiber}g)")
            score += 10

        # Analyze sodium
        sodium = extract_nutrition_value(nutrition, 'sodium')
        if sodium > 400:
            cons.append(f"High sodium ({sodium}mg)")
            score -= 10

        # Ensure we have content
        if not pros:
            pros.append("Contains essential nutrients")
        if not cons:
            cons.append("Review serving size for daily intake")

        score = max(0, min(100, score))

        calories = extract_nutrition_value(nutrition, 'calories')
        summary = f"This {product.name} has {calories} calories per serving with {protein}g protein. "
        summary += "Overall, it appears to be a nutritious choice for your health goals!" if score >= 70 else \
                   "It has some nutritional benefits but should be consumed mindfully." if score >= 50 else \
                   "Consider healthier alternatives or consume in moderation."

        return {
            "score": score,
            "summary": summary,
            "pros": pros[:3],
            "cons": cons[:3]
        }

    def _no_nutrition_response(self) -> Dict:
        """Response when nutrition info unavailable."""
        return {
            "score": 0,
            "summary": "I can't evaluate the health alignment without nutrition information for this product.",
            "pros": ["N/A"],
            "cons": ["Missing nutrition data"]
        }
