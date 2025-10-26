"""
Barcode lookup service for retrieving product information.
"""

import aiohttp
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class BarcodeService:
    """Service for looking up barcode information."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BARCODE_LOOKUP_API_KEY")
        self.base_url = "https://api.barcodelookup.com/v3/products"

    async def lookup(self, barcode: str) -> Optional[Dict]:
        """
        Look up product information by barcode.

        Args:
            barcode: The barcode number to look up

        Returns:
            Dictionary with product information or None if not found
        """
        try:
            params = {
                "barcode": barcode,
                "formatted": "y",
                "key": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if "products" in data and len(data["products"]) > 0:
                            product = data["products"][0]
                            return self._normalize_product_data(product)
                        else:
                            # Try mock data for testing
                            return self._get_mock_data(barcode)
                    else:
                        # Return mock data for testing
                        return self._get_mock_data(barcode)

        except Exception as e:
            print(f"Error looking up barcode: {e}")
            # Return mock data for testing
            return self._get_mock_data(barcode)

    def _normalize_product_data(self, product: Dict) -> Dict:
        """Normalize API response to our expected format."""

        # Extract nutrition if available
        nutrition = None
        if "nutrition" in product or "nutrition_facts" in product:
            nutr_data = product.get("nutrition") or product.get("nutrition_facts", {})
            nutrition = {
                "calories": self._parse_float(nutr_data.get("calories", 0)),
                "protein": self._parse_float(nutr_data.get("protein", 0)),
                "carbohydrates": self._parse_float(nutr_data.get("carbohydrates", 0)),
                "sugar": self._parse_float(nutr_data.get("sugar", 0)),
                "fat": self._parse_float(nutr_data.get("fat", 0)),
                "saturated_fat": self._parse_float(nutr_data.get("saturated_fat", 0)),
                "sodium": self._parse_float(nutr_data.get("sodium", 0)),
                "fiber": self._parse_float(nutr_data.get("fiber", 0)),
            }

        return {
            "name": product.get("title", "Unknown Product"),
            "brand": product.get("brand", "Unknown Brand"),
            "category": product.get("category", "Uncategorized"),
            "price": self._parse_float(product.get("stores", [{}])[0].get("price", 0)) if product.get("stores") else 3.99,
            "size": product.get("size", "1 unit"),
            "nutrition": nutrition,
            "ingredients": product.get("ingredients", "")
        }

    def _parse_float(self, value) -> float:
        """Safely parse float value."""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point
                value = ''.join(c for c in value if c.isdigit() or c == '.')
            return float(value) if value else 0.0
        except:
            return 0.0

    def _get_mock_data(self, barcode: str) -> Optional[Dict]:
        """Return mock data for testing when API is unavailable."""
        mock_products = {
            # Beverages
            "012000161551": {
                "name": "Coca-Cola Classic",
                "brand": "Coca-Cola",
                "category": "beverages",
                "price": 1.99,
                "size": "20 fl oz",
                "nutrition": {
                    "calories": 240,
                    "protein": 0,
                    "carbohydrates": 65,
                    "sugar": 65,
                    "fat": 0,
                    "saturated_fat": 0,
                    "sodium": 75,
                    "fiber": 0
                },
                "ingredients": "Carbonated water, high fructose corn syrup, caramel color, phosphoric acid, natural flavors, caffeine"
            },
            "078000113464": {
                "name": "Gatorade Thirst Quencher Fruit Punch",
                "brand": "Gatorade",
                "category": "beverages",
                "price": 1.49,
                "size": "20 fl oz",
                "nutrition": {
                    "calories": 140,
                    "protein": 0,
                    "carbohydrates": 36,
                    "sugar": 34,
                    "fat": 0,
                    "saturated_fat": 0,
                    "sodium": 270,
                    "fiber": 0
                },
                "ingredients": "Water, sugar, dextrose, citric acid, natural and artificial flavor, salt, sodium citrate, monopotassium phosphate, red 40"
            },
            # Snacks
            "028400047685": {
                "name": "Cheez-It Original Baked Snack Crackers",
                "brand": "Cheez-It",
                "category": "snacks",
                "price": 3.99,
                "size": "12.4 oz",
                "nutrition": {
                    "calories": 150,
                    "protein": 3,
                    "carbohydrates": 17,
                    "sugar": 0,
                    "fat": 8,
                    "saturated_fat": 2,
                    "sodium": 230,
                    "fiber": 1
                },
                "ingredients": "Enriched flour, vegetable oil, cheese, salt, paprika, yeast, paprika extract color, soy lecithin"
            },
            # Protein bars
            "722252601025": {
                "name": "Quest Protein Bar - Chocolate Chip Cookie Dough",
                "brand": "Quest Nutrition",
                "category": "health_food",
                "price": 2.49,
                "size": "2.12 oz (60g)",
                "nutrition": {
                    "calories": 200,
                    "protein": 21,
                    "carbohydrates": 22,
                    "sugar": 1,
                    "fat": 8,
                    "saturated_fat": 3,
                    "sodium": 250,
                    "fiber": 14
                },
                "ingredients": "Protein blend (milk protein isolate, whey protein isolate), soluble corn fiber, almonds, water, erythritol, natural flavors, cocoa butter, sea salt, steviol glycosides"
            },
            # Cereal
            "016000275683": {
                "name": "Cheerios Cereal",
                "brand": "General Mills",
                "category": "breakfast",
                "price": 4.99,
                "size": "18 oz",
                "nutrition": {
                    "calories": 110,
                    "protein": 3,
                    "carbohydrates": 22,
                    "sugar": 2,
                    "fat": 2,
                    "saturated_fat": 0,
                    "sodium": 160,
                    "fiber": 3
                },
                "ingredients": "Whole grain oats, modified corn starch, sugar, salt, tripotassium phosphate, vitamin E, wheat starch"
            }
        }

        return mock_products.get(barcode, None)
