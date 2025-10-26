"""
Data models for the Nutrition AI Agent system.
"""

from typing import Optional, Dict, List
from pydantic import BaseModel


class Product(BaseModel):
    """Product data model representing scanned items."""
    barcode: str
    name: str
    brand: str
    category: str
    price: float
    size: Optional[str] = None
    unit_price: Optional[float] = None
    nutrition: Optional[Dict[str, float]] = None
    ingredients: Optional[str] = None

    def get_nutrition_value(self, key: str) -> float:
        """Safely get nutrition value."""
        if not self.nutrition:
            return 0.0
        return self.nutrition.get(key, 0.0)

    def has_nutrition_info(self) -> bool:
        """Check if product has nutrition information."""
        return self.nutrition is not None and len(self.nutrition) > 0


class UserProfile(BaseModel):
    """User profile with health and fitness goals."""
    health_goals: str
    fitness_goals: str
    dietary_restrictions: str = ""

    # Additional user data
    height_cm: Optional[float] = None
    current_weight_kg: Optional[float] = None
    goal_type: Optional[str] = None
    activity_level: Optional[str] = None
    diet_type: Optional[str] = None
    daily_calorie_target: Optional[int] = None
    daily_protein_target_g: Optional[int] = None
    daily_carbs_target_g: Optional[int] = None
    daily_fat_target_g: Optional[int] = None

    def get_health_goals_list(self) -> List[str]:
        """Parse health goals into list."""
        return [goal.strip().lower() for goal in self.health_goals.split(",") if goal.strip()]

    def get_fitness_goals_list(self) -> List[str]:
        """Parse fitness goals into list."""
        return [goal.strip().lower() for goal in self.fitness_goals.split(",") if goal.strip()]

    def get_restrictions_list(self) -> List[str]:
        """Parse dietary restrictions into list."""
        if not self.dietary_restrictions:
            return []
        return [r.strip().lower() for r in self.dietary_restrictions.split(",") if r.strip()]


class EvaluationResult(BaseModel):
    """Result from an evaluation agent."""
    score: float  # 0-100
    summary: str
    details: Dict
    recommendations: List[str] = []
