"""
Service layer for backend integration.
Provides backward compatibility with existing Flask API.
"""

import asyncio
from typing import Dict, Optional
from agent.main_agent import get_agent
from agent.models import Product, UserProfile


class NutritionAgentService:
    """
    Service class for Flask backend integration.
    Wraps the main NutritionAgent with a backward-compatible interface.
    """

    def __init__(self):
        """Initialize the service with the main agent."""
        self.agent = get_agent()

    async def scan_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Scan a barcode and return product information.

        Args:
            barcode: Barcode number to scan

        Returns:
            Product dictionary or None if not found
        """
        try:
            product = await self.agent.scan_barcode(barcode)

            if not product:
                return None

            return {
                "barcode": product.barcode,
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "price": product.price,
                "size": product.size,
                "unit_price": product.unit_price,
                "nutrition": product.nutrition or {},
                "ingredients": product.ingredients
            }

        except Exception as e:
            print(f"Error scanning barcode: {e}")
            return None

    async def evaluate_product(
        self,
        product_data: Dict,
        user_profile_data: Dict
    ) -> Dict:
        """
        Evaluate a product comprehensively.

        Args:
            product_data: Product information dictionary
            user_profile_data: User profile dictionary

        Returns:
            Complete evaluation with all analyses
        """
        try:
            # Convert dicts to models
            product = self._dict_to_product(product_data)
            user_profile = self._dict_to_user_profile(user_profile_data)

            # Evaluate using main agent
            return await self.agent.evaluate_product(product, user_profile)

        except Exception as e:
            print(f"Error evaluating product: {e}")
            return self._error_response()

    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Chat with the AI companion.

        Args:
            message: User's message
            context: Optional context

        Returns:
            AI response
        """
        return await self.agent.chat(message, context)

    def _dict_to_product(self, data: Dict) -> Product:
        """Convert dictionary to Product model."""
        return Product(
            barcode=data.get("barcode", ""),
            name=data.get("name", "Unknown Product"),
            brand=data.get("brand", "Unknown Brand"),
            category=data.get("category", "Uncategorized"),
            price=float(data.get("price", 0)),
            size=data.get("size"),
            unit_price=data.get("unit_price"),
            nutrition=data.get("nutrition"),
            ingredients=data.get("ingredients")
        )

    def _dict_to_user_profile(self, data: Dict) -> UserProfile:
        """Convert dictionary to UserProfile model."""
        health_goals = self._build_health_goals(data)
        fitness_goals = self._build_fitness_goals(data)
        restrictions = self._build_restrictions(data)

        return UserProfile(
            health_goals=health_goals,
            fitness_goals=fitness_goals,
            dietary_restrictions=restrictions,
            height_cm=data.get("height_cm"),
            current_weight_kg=data.get("current_weight_kg"),
            goal_type=data.get("goal_type"),
            activity_level=data.get("activity_level"),
            diet_type=data.get("diet_type"),
            daily_calorie_target=data.get("daily_calorie_target"),
            daily_protein_target_g=data.get("daily_protein_target_g"),
            daily_carbs_target_g=data.get("daily_carbs_target_g"),
            daily_fat_target_g=data.get("daily_fat_target_g")
        )

    def _build_health_goals(self, data: Dict) -> str:
        """Build health goals string from profile data."""
        goals = []

        goal_type = data.get("goal_type", "").replace("_", " ")
        if goal_type:
            goals.append(goal_type)

        diet_type = data.get("diet_type", "")
        if diet_type and diet_type != "standard":
            goals.append(diet_type)

        if data.get("daily_calorie_target"):
            goals.append(f"target {data['daily_calorie_target']} calories")

        return ", ".join(goals) if goals else "general health"

    def _build_fitness_goals(self, data: Dict) -> str:
        """Build fitness goals string from profile data."""
        goals = []

        activity_level = data.get("activity_level", "").replace("_", " ")
        if activity_level:
            goals.append(activity_level)

        goal_type = data.get("goal_type", "")
        if "muscle" in goal_type.lower():
            goals.append("muscle building")
        elif "loss" in goal_type.lower():
            goals.append("weight loss")
        elif "gain" in goal_type.lower():
            goals.append("weight gain")

        protein_target = data.get("daily_protein_target_g", 0)
        if protein_target and protein_target > 100:
            goals.append("high protein diet")

        return ", ".join(goals) if goals else "general fitness"

    def _build_restrictions(self, data: Dict) -> str:
        """Build dietary restrictions string."""
        restrictions = []

        if data.get("allergies"):
            allergies = data["allergies"].split(",")
            restrictions.extend([f"no {a.strip()}" for a in allergies if a.strip()])

        if data.get("dietary_restrictions"):
            restrictions.append(data["dietary_restrictions"])

        return ", ".join(restrictions)

    def _error_response(self) -> Dict:
        """Generate error response."""
        return {
            "product": {},
            "health_analysis": {"score": 0, "summary": "Error", "error": True},
            "fitness_analysis": {"score": 0, "summary": "Error", "error": True},
            "price_analysis": {"score": 0, "summary": "Error", "error": True},
            "overall": {
                "score": 0,
                "recommendation": "Error",
                "recommendation_emoji": "❌"
            },
            "companion_message": "Sorry, I encountered an error. Please try again!",
            "error": True
        }

    def is_available(self) -> bool:
        """Check if service is available."""
        return self.agent is not None


# Singleton instance
_service_instance = None


def get_nutrition_agent_service() -> NutritionAgentService:
    """Get or create singleton service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = NutritionAgentService()
    return _service_instance


def run_async(coro):
    """
    Run async code from synchronous Flask routes.

    Args:
        coro: Coroutine to run

    Returns:
        Result of the coroutine
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
