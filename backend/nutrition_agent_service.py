#!/usr/bin/env python3
"""
Nutrition Agent Service - Integration Layer
Connects the nutrition_agent system with the existing backend API.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional
import asyncio

# Add nutrition_agent to path
nutrition_agent_path = Path(__file__).parent.parent / "nutrition_agent"
sys.path.insert(0, str(nutrition_agent_path))

from agents.barcode_scanner import BarcodeScannerAgent
from agents.price_evaluator import PriceEvaluatorAgent
from agents.health_evaluator import HealthEvaluatorAgent
from agents.fitness_evaluator import FitnessEvaluatorAgent
from services.llm_service import LLMService
from services.barcode_api import BarcodeAPIService
from models.user_profile import UserProfile
from models.product import Product


class NutritionAgentService:
    """
    Service class to integrate nutrition-agent with the Flask backend.
    Provides a clean interface for barcode scanning and AI-powered evaluation.
    """

    def __init__(self, anthropic_api_key: str = None, barcode_api_key: str = None):
        """
        Initialize the nutrition agent service.

        Args:
            anthropic_api_key: API key for Claude/Anthropic (for AI analysis)
            barcode_api_key: API key for barcode lookup service
        """
        # Get API keys from environment or parameters
        self.anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.barcode_key = barcode_api_key or os.getenv("BARCODE_LOOKUP_API_KEY")

        # Initialize services
        self.llm_service = None
        self.barcode_service = None

        # Initialize agents
        self.scanner_agent = None
        self.price_agent = None
        self.health_agent = None
        self.fitness_agent = None

        self._initialize_services()

    def _initialize_services(self):
        """Initialize all services and agents"""
        try:
            # Initialize core services
            if self.anthropic_key:
                self.llm_service = LLMService(api_key=self.anthropic_key)

            if self.barcode_key:
                self.barcode_service = BarcodeAPIService(api_key=self.barcode_key)

            # Initialize agents
            if self.barcode_service:
                self.scanner_agent = BarcodeScannerAgent(self.barcode_service)

            if self.llm_service:
                self.price_agent = PriceEvaluatorAgent(self.llm_service)
                self.health_agent = HealthEvaluatorAgent(self.llm_service)
                self.fitness_agent = FitnessEvaluatorAgent(self.llm_service)

        except Exception as e:
            print(f"Warning: Failed to initialize nutrition agent services: {e}")

    async def scan_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Scan a barcode and return product information.

        Args:
            barcode: The barcode number to scan

        Returns:
            Dictionary with product data or None if not found
        """
        if not self.scanner_agent:
            raise Exception("Barcode scanner not initialized. Check BARCODE_LOOKUP_API_KEY.")

        try:
            product = await self.scanner_agent.scan(barcode)

            if not product:
                return None

            # Convert Product model to dictionary
            return self._product_to_dict(product)

        except Exception as e:
            print(f"Error scanning barcode: {e}")
            return None

    async def evaluate_product(
        self,
        product_data: Dict,
        user_profile_data: Dict
    ) -> Dict:
        """
        Evaluate a product using health, price, and fitness agents.

        Args:
            product_data: Product information (from barcode scan or manual input)
            user_profile_data: User's goals and preferences from database

        Returns:
            Dictionary with comprehensive evaluation from all agents
        """
        try:
            # Convert dict to Product model
            product = self._dict_to_product(product_data)

            # Convert dict to UserProfile model
            user_profile = self._dict_to_user_profile(user_profile_data)

            # Run all evaluations in parallel for performance
            health_analysis, price_analysis, fitness_analysis = await asyncio.gather(
                self._evaluate_health(product, user_profile),
                self._evaluate_price(product),
                self._evaluate_fitness(product, user_profile),
                return_exceptions=True
            )

            # Handle any errors
            if isinstance(health_analysis, Exception):
                health_analysis = self._error_response("health")
            if isinstance(price_analysis, Exception):
                price_analysis = self._error_response("price")
            if isinstance(fitness_analysis, Exception):
                fitness_analysis = self._error_response("fitness")

            # Calculate overall score
            health_score = health_analysis.get("score", 0)
            fitness_score = fitness_analysis.get("score", 0)
            overall_score = (health_score + fitness_score) / 2

            # Determine overall recommendation
            if overall_score >= 70:
                recommendation = "Highly Recommended"
                recommendation_emoji = "✅"
            elif overall_score >= 50:
                recommendation = "Acceptable with Caution"
                recommendation_emoji = "⚠️"
            else:
                recommendation = "Not Recommended"
                recommendation_emoji = "❌"

            return {
                "product": self._product_to_dict(product),
                "health_analysis": health_analysis,
                "price_analysis": price_analysis,
                "fitness_analysis": fitness_analysis,
                "overall": {
                    "score": round(overall_score, 1),
                    "recommendation": recommendation,
                    "recommendation_emoji": recommendation_emoji
                }
            }

        except Exception as e:
            print(f"Error evaluating product: {e}")
            return self._error_evaluation_response()

    async def _evaluate_health(self, product: Product, user_profile: UserProfile) -> Dict:
        """Evaluate health alignment"""
        if not self.health_agent:
            return self._error_response("health")
        return await self.health_agent.evaluate(product, user_profile)

    async def _evaluate_price(self, product: Product) -> Dict:
        """Evaluate price value"""
        if not self.price_agent:
            return self._error_response("price")
        return await self.price_agent.evaluate(product)

    async def _evaluate_fitness(self, product: Product, user_profile: UserProfile) -> Dict:
        """Evaluate fitness alignment"""
        if not self.fitness_agent:
            return self._error_response("fitness")
        return await self.fitness_agent.evaluate(product, user_profile)

    def _product_to_dict(self, product: Product) -> Dict:
        """Convert Product model to dictionary"""
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

    def _dict_to_product(self, data: Dict) -> Product:
        """Convert dictionary to Product model"""
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
        """Convert dictionary (from database) to UserProfile model"""
        # Map database fields to UserProfile fields
        health_goals = self._build_health_goals_string(data)
        fitness_goals = self._build_fitness_goals_string(data)
        dietary_restrictions = self._build_restrictions_string(data)

        return UserProfile(
            health_goals=health_goals,
            fitness_goals=fitness_goals,
            dietary_restrictions=dietary_restrictions
        )

    def _build_health_goals_string(self, profile_data: Dict) -> str:
        """Build health goals string from database profile"""
        goals = []

        goal_type = profile_data.get("goal_type", "").replace("_", " ")
        if goal_type:
            goals.append(goal_type)

        diet_type = profile_data.get("diet_type", "")
        if diet_type and diet_type != "standard":
            goals.append(diet_type)

        # Add any specific health targets
        if profile_data.get("daily_calorie_target"):
            goals.append(f"target {profile_data['daily_calorie_target']} calories")

        return ", ".join(goals) if goals else "general health"

    def _build_fitness_goals_string(self, profile_data: Dict) -> str:
        """Build fitness goals string from database profile"""
        goals = []

        activity_level = profile_data.get("activity_level", "").replace("_", " ")
        if activity_level:
            goals.append(activity_level)

        goal_type = profile_data.get("goal_type", "")
        if "muscle" in goal_type.lower():
            goals.append("muscle building")
        elif "loss" in goal_type.lower():
            goals.append("weight loss")
        elif "gain" in goal_type.lower() and "muscle" not in goal_type.lower():
            goals.append("weight gain")

        # Add protein target if high
        protein_target = profile_data.get("daily_protein_target_g", 0)
        if protein_target and protein_target > 100:
            goals.append("high protein diet")

        return ", ".join(goals) if goals else "general fitness"

    def _build_restrictions_string(self, profile_data: Dict) -> str:
        """Build dietary restrictions string from database profile"""
        restrictions = []

        if profile_data.get("allergies"):
            allergies = profile_data["allergies"].split(",")
            restrictions.extend([f"no {a.strip()}" for a in allergies if a.strip()])

        if profile_data.get("dietary_restrictions"):
            restrictions.append(profile_data["dietary_restrictions"])

        return ", ".join(restrictions)

    def _error_response(self, evaluation_type: str) -> Dict:
        """Return error response for a specific evaluation type"""
        return {
            "score": 0,
            "summary": f"{evaluation_type.title()} evaluation unavailable. Agent not initialized.",
            "error": True
        }

    def _error_evaluation_response(self) -> Dict:
        """Return error response for full evaluation"""
        return {
            "product": {},
            "health_analysis": self._error_response("health"),
            "price_analysis": self._error_response("price"),
            "fitness_analysis": self._error_response("fitness"),
            "overall": {
                "score": 0,
                "recommendation": "Error",
                "recommendation_emoji": "❌"
            },
            "error": "Failed to evaluate product"
        }

    def is_available(self) -> bool:
        """Check if the service is properly initialized and available"""
        return (self.scanner_agent is not None and
                self.health_agent is not None and
                self.fitness_agent is not None and
                self.price_agent is not None)


# Singleton instance for the Flask app
_nutrition_agent_service = None


def get_nutrition_agent_service() -> NutritionAgentService:
    """
    Get or create the nutrition agent service singleton.

    Returns:
        NutritionAgentService instance
    """
    global _nutrition_agent_service

    if _nutrition_agent_service is None:
        _nutrition_agent_service = NutritionAgentService()

    return _nutrition_agent_service


# Async helper for Flask synchronous routes
def run_async(coro):
    """
    Helper function to run async code from synchronous Flask routes.

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
