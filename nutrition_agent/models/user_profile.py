from pydantic import BaseModel
from typing import List


class UserProfile(BaseModel):
    """User profile with health and fitness goals"""
    health_goals: str
    fitness_goals: str
    dietary_restrictions: str = ""
    
    def get_health_goals_list(self) -> List[str]:
        """Parse health goals into list"""
        return [goal.strip().lower() for goal in self.health_goals.split(",") if goal.strip()]
    
    def get_fitness_goals_list(self) -> List[str]:
        """Parse fitness goals into list"""
        return [goal.strip().lower() for goal in self.fitness_goals.split(",") if goal.strip()]
    
    def get_restrictions_list(self) -> List[str]:
        """Parse dietary restrictions into list"""
        if not self.dietary_restrictions:
            return []
        return [r.strip().lower() for r in self.dietary_restrictions.split(",") if r.strip()]