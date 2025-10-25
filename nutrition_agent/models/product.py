from typing import Optional, Dict
from pydantic import BaseModel


class Product(BaseModel):
    """Product data model"""
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
        """Safely get nutrition value"""
        if not self.nutrition:
            return 0.0
        return self.nutrition.get(key, 0.0)
    
    def has_nutrition_info(self) -> bool:
        """Check if product has nutrition information"""
        return self.nutrition is not None and len(self.nutrition) > 0
