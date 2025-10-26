#!/usr/bin/env python3
"""
Nutrition Agent Service - Integration Layer
Connects the NEW agent system with the existing backend API.
Updated to use the new integrated agent in the 'agent' directory.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional
import asyncio

# Add the new agent directory to path
agent_path = Path(__file__).parent.parent / "agent"
sys.path.insert(0, str(agent_path))

# Import from the NEW agent system
from agent.service import get_nutrition_agent_service as get_new_service, run_async


class NutritionAgentService:
    """
    Service class to integrate the NEW nutrition agent with the Flask backend.
    Provides a clean interface for barcode scanning and AI-powered evaluation.

    This is a wrapper around the new agent system for backward compatibility.
    """

    def __init__(self):
        """
        Initialize the nutrition agent service.

        Uses Google Gemini API (configured via agent/.env file).
        """
        # Initialize the new agent service
        self._new_service = get_new_service()


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
            # Delegate to the new agent service
            return await self._new_service.evaluate_product(product_data, user_profile_data)
        except Exception as e:
            print(f"Error evaluating product: {e}")
            return self._error_evaluation_response()

    async def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Chat with the AI nutrition companion.

        Args:
            message: User's message
            context: Optional context (user profile, recent product)

        Returns:
            AI response string
        """
        try:
            # Delegate to the new agent service
            return await self._new_service.chat(message, context)
        except Exception as e:
            print(f"Error in chat: {e}")
            return "Sorry, I encountered an error. Please try again!"

    def _error_evaluation_response(self) -> Dict:
        """Return error response for full evaluation"""
        return {
            "product": {},
            "health_analysis": {"score": 0, "summary": "Error", "error": True},
            "price_analysis": {"score": 0, "summary": "Error", "error": True},
            "fitness_analysis": {"score": 0, "summary": "Error", "error": True},
            "overall": {
                "score": 0,
                "recommendation": "Error",
                "recommendation_emoji": "❌"
            },
            "companion_message": "Sorry, I encountered an error. Please try again!",
            "error": "Failed to evaluate product"
        }

    def is_available(self) -> bool:
        """Check if the service is properly initialized and available"""
        return self._new_service is not None and self._new_service.is_available()


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
