"""
Nutrition AI Agent Package
A comprehensive AI companion for nutrition evaluation and personalized recommendations.

Version: 2.0.0 - Production Ready
"""

# Main agent
from agent.main_agent import NutritionAgent, get_agent

# Evaluators
from agent.health_evaluator import HealthEvaluator
from agent.fitness_evaluator import FitnessEvaluator
from agent.price_evaluator import PriceEvaluator

# Models
from agent.models import Product, UserProfile, EvaluationResult

# Utilities
from agent.utils.data_parser import parse_nutrition_data, calculate_macros
from agent.utils.response_formatter import format_evaluation_response, format_error_response

# Backend integration (for backward compatibility)
from agent.service import get_nutrition_agent_service, run_async, NutritionAgentService

__version__ = "2.0.0"

__all__ = [
    # Main agent
    'NutritionAgent',
    'get_agent',

    # Evaluators
    'HealthEvaluator',
    'FitnessEvaluator',
    'PriceEvaluator',

    # Models
    'Product',
    'UserProfile',
    'EvaluationResult',

    # Utilities
    'parse_nutrition_data',
    'calculate_macros',
    'format_evaluation_response',
    'format_error_response',

    # Backend integration (backward compatibility)
    'get_nutrition_agent_service',
    'run_async',
    'NutritionAgentService',
]
