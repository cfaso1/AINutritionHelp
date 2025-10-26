"""
Main Nutrition AI Agent
A conversational AI companion for personalized nutrition evaluation.

This is the central orchestrator that coordinates all evaluators and provides
a unified interface for the Nutrition AI application.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports when running directly
if __name__ == "__main__":
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

from typing import Dict, Optional
from dotenv import load_dotenv
from google import genai

from agent.models import Product, UserProfile
from agent.barcode_service import BarcodeService
from agent.fitness_evaluator import FitnessEvaluator
from agent.health_evaluator import HealthEvaluator
from agent.price_evaluator import PriceEvaluator
from agent.utils.response_formatter import format_evaluation_response, format_error_response

# Load .env from agent directory
_agent_dir = Path(__file__).parent
load_dotenv(_agent_dir / '.env')


class NutritionAgent:
    """
    Main Nutrition AI Agent that coordinates all evaluation components.

    Features:
    - Barcode scanning and product lookup
    - Health evaluation (nutritional analysis)
    - Fitness evaluation (workout and activity recommendations)
    - Price evaluation (value for money analysis)
    - Conversational AI companion behavior
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize the Nutrition AI Agent.

        Args:
            model_name: Google Gemini model to use
        """
        self.model_name = model_name
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        # Initialize services
        self.barcode_service = BarcodeService()

        # Initialize evaluators
        self.health_evaluator = HealthEvaluator(self.model_name)
        self.fitness_evaluator = FitnessEvaluator(self.model_name)
        self.price_evaluator = PriceEvaluator(self.model_name)

    async def scan_barcode(self, barcode: str) -> Optional[Product]:
        """
        Scan a barcode and retrieve product information.

        Args:
            barcode: Barcode number to scan

        Returns:
            Product object if found, None otherwise
        """
        try:
            product_data = await self.barcode_service.lookup(barcode)

            if not product_data:
                return None

            return Product(
                barcode=barcode,
                name=product_data.get("name", "Unknown Product"),
                brand=product_data.get("brand", "Unknown Brand"),
                category=product_data.get("category", "Uncategorized"),
                price=product_data.get("price", 0.0),
                size=product_data.get("size"),
                unit_price=product_data.get("unit_price"),
                nutrition=product_data.get("nutrition"),
                ingredients=product_data.get("ingredients")
            )

        except Exception as e:
            print(f"Error scanning barcode: {e}")
            return None

    async def evaluate_product(
        self,
        product: Product,
        user_profile: UserProfile
    ) -> Dict:
        """
        Perform comprehensive product evaluation.

        Evaluates the product using all three evaluators and generates
        a personalized companion message.

        Args:
            product: Product to evaluate
            user_profile: User's health and fitness goals

        Returns:
            Complete evaluation with scores, analysis, and companion message
        """
        try:
            # Run all evaluations in parallel
            import asyncio
            results = await asyncio.gather(
                self.health_evaluator.evaluate(product, user_profile),
                self.fitness_evaluator.evaluate(product, user_profile),
                self.price_evaluator.evaluate(product),
                return_exceptions=True
            )

            health_analysis, fitness_analysis, price_analysis = results

            # Handle any errors in individual evaluations
            if isinstance(health_analysis, Exception):
                health_analysis = {'score': 0, 'summary': 'Health evaluation failed', 'pros': [], 'cons': [], 'error': True}
            if isinstance(fitness_analysis, Exception):
                fitness_analysis = {'score': 0, 'summary': 'Fitness evaluation failed', 'best_for': 'N/A', 'recommendation': '', 'error': True}
            if isinstance(price_analysis, Exception):
                price_analysis = {'score': 0, 'summary': 'Price evaluation failed', 'rating': 'Unknown', 'error': True}

            # Generate personalized companion message
            companion_message = await self._generate_companion_message(
                product,
                user_profile,
                health_analysis,
                fitness_analysis,
                price_analysis
            )

            # Format and return complete response
            product_dict = {
                'barcode': product.barcode,
                'name': product.name,
                'brand': product.brand,
                'category': product.category,
                'price': product.price,
                'size': product.size,
                'nutrition': product.nutrition or {}
            }

            return format_evaluation_response(
                product_dict,
                health_analysis,
                fitness_analysis,
                price_analysis,
                companion_message
            )

        except Exception as e:
            print(f"Error evaluating product: {e}")
            return format_error_response(
                "I encountered an error while evaluating this product. Please try again!"
            )

    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Interactive chat with the AI companion.

        Provides personalized nutrition advice based on context.

        Args:
            message: User's message
            context: Optional context (user profile, recent scans, etc.)

        Returns:
            AI companion's response
        """
        context_str = self._build_context_string(context)

        prompt = f"""You are a friendly, knowledgeable AI nutrition companion helping users achieve their health and fitness goals.

{context_str}

User's message: {message}

Respond in a warm, conversational, and supportive way. Provide helpful, actionable advice. Keep it friendly and encouraging!"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I'm having trouble responding right now. Could you try asking again?"

    async def _generate_companion_message(
        self,
        product: Product,
        user_profile: UserProfile,
        health_analysis: Dict,
        fitness_analysis: Dict,
        price_analysis: Dict
    ) -> str:
        """Generate personalized companion message synthesizing all analyses."""

        overall_score = (health_analysis.get('score', 0) + fitness_analysis.get('score', 0)) / 2

        prompt = f"""You are a friendly, supportive AI nutrition companion helping users make informed food choices.

USER PROFILE:
- Health Goals: {user_profile.health_goals}
- Fitness Goals: {user_profile.fitness_goals}
- Dietary Restrictions: {user_profile.dietary_restrictions or 'None'}
- Daily Calorie Target: {user_profile.daily_calorie_target or 'Not specified'} cal
- Daily Protein Target: {user_profile.daily_protein_target_g or 'Not specified'}g

PRODUCT:
{product.name} by {product.brand}
Price: ${product.price}
{f'Nutrition: Calories {product.nutrition.get("calories", 0)}, Protein {product.nutrition.get("protein", 0)}g, Sugar {product.nutrition.get("sugar", 0)}g' if product.nutrition else 'No nutrition info'}

ANALYSIS RESULTS:
Health Score: {health_analysis.get('score', 0)}/100
Health Summary: {health_analysis.get('summary', '')}
Pros: {', '.join(health_analysis.get('pros', []))}
Cons: {', '.join(health_analysis.get('cons', []))}

Fitness Score: {fitness_analysis.get('score', 0)}/100
Fitness Summary: {fitness_analysis.get('summary', '')}
Best For: {fitness_analysis.get('best_for', '')}

Price Rating: {price_analysis.get('rating', '')}
Price Summary: {price_analysis.get('summary', '')}

Overall Score: {overall_score}/100

Write a friendly, conversational message (3-4 paragraphs) that:
1. Warmly acknowledges what they scanned
2. Explains how it aligns with THEIR SPECIFIC goals
3. Provides actionable recommendations (timing, portions, pairings)
4. Includes pricing insights
5. Ends with encouragement

Be personal and supportive - like a knowledgeable friend, not a clinical report!"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating companion message: {e}")
            return self._generate_fallback_message(product, overall_score, health_analysis, fitness_analysis)

    def _generate_fallback_message(
        self,
        product: Product,
        overall_score: float,
        health_analysis: Dict,
        fitness_analysis: Dict
    ) -> str:
        """Generate basic companion message when AI fails."""
        tone = "Great choice!" if overall_score >= 70 else "This could work with considerations." if overall_score >= 50 else "Let's explore better options."

        return f"""Hey! I see you scanned {product.name} by {product.brand}. {tone}

{health_analysis.get('summary', 'Unable to analyze health benefits.')}

{fitness_analysis.get('summary', 'Unable to analyze fitness alignment.')}

{fitness_analysis.get('recommendation', 'Keep working towards your goals!')}

I'm here to help you make informed choices for your health journey. Keep it up! 💪"""

    def _build_context_string(self, context: Optional[Dict]) -> str:
        """Build context string for chat."""
        if not context:
            return ""

        context_parts = []

        if "user_profile" in context:
            profile = context["user_profile"]

            # Add user's physical stats
            profile_info = []

            # Gender
            if profile.get('gender'):
                gender_display = profile['gender'].capitalize()
                profile_info.append(f"Gender: {gender_display}")

            # Age category
            if profile.get('age_category'):
                profile_info.append(f"Age: {profile['age_category']}")

            # Height in imperial units
            if profile.get('height_feet') is not None and profile.get('height_inches') is not None:
                profile_info.append(f"Height: {profile['height_feet']}'{profile['height_inches']}\"")
            elif profile.get('height_cm'):
                total_inches = profile['height_cm'] / 2.54
                feet = int(total_inches // 12)
                inches = int(total_inches % 12)
                profile_info.append(f"Height: {feet}'{inches}\"")

            # Weight in imperial units
            if profile.get('weight_lbs'):
                profile_info.append(f"Weight: {profile['weight_lbs']} lbs")
            elif profile.get('current_weight_kg'):
                lbs = round(profile['current_weight_kg'] / 0.453592)
                profile_info.append(f"Weight: {lbs} lbs")

            # BMI
            if profile.get('bmi'):
                profile_info.append(f"BMI: {profile['bmi']}")

            # Activity level
            if profile.get('activity_level'):
                activity = profile['activity_level'].replace('_', ' ')
                profile_info.append(f"Activity level: {activity}")

            # Goals and diet type
            if profile.get('goal_type'):
                goal = profile['goal_type'].replace('_', ' ')
                profile_info.append(f"Goal: {goal}")

            if profile.get('diet_type') and profile['diet_type'] != 'standard':
                profile_info.append(f"Diet type: {profile['diet_type']}")

            # Nutritional targets
            if profile.get('daily_calorie_target'):
                profile_info.append(f"Daily calorie target: {profile['daily_calorie_target']} cal")

            if profile.get('daily_protein_target_g'):
                profile_info.append(f"Daily protein target: {profile['daily_protein_target_g']}g")

            # Dietary restrictions
            if profile.get('allergies'):
                profile_info.append(f"Allergies: {profile['allergies']}")

            if profile.get('dietary_restrictions'):
                profile_info.append(f"Dietary restrictions: {profile['dietary_restrictions']}")

            if profile_info:
                context_parts.append("USER PROFILE:\n" + "\n".join(f"- {info}" for info in profile_info))

        if "recent_product" in context:
            product = context["recent_product"]
            context_parts.append(f"\nRecently scanned: {product.get('name', 'Unknown')}")

        return "\n".join(context_parts) if context_parts else ""


# Singleton instance
_agent_instance = None


def get_agent() -> NutritionAgent:
    """Get or create singleton Nutrition Agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = NutritionAgent()
    return _agent_instance
