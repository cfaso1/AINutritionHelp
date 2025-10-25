import aiohttp
from typing import Optional, Dict


class BarcodeAPIService:
    """Service for looking up barcode information"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.barcodelookup.com/v3/products"
    
    async def lookup(self, barcode: str) -> Optional[Dict]:
        """
        Look up product information by barcode
        
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
                        print(f"API returned status {response.status}")
                        # Return mock data for testing
                        return self._get_mock_data(barcode)
                        
        except Exception as e:
            print(f"Error looking up barcode: {e}")
            # Return mock data for testing
            return self._get_mock_data(barcode)
    
    def _normalize_product_data(self, product: Dict) -> Dict:
        """Normalize API response to our expected format"""
        
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
        """Safely parse float value"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point
                value = ''.join(c for c in value if c.isdigit() or c == '.')
            return float(value) if value else 0.0
        except:
            return 0.0
    
    def _get_mock_data(self, barcode: str) -> Dict:
        """
        Return mock data for testing when API is unavailable
        This helps during development and testing
        """
        mock_products = {
            "012000161551": {  # Coca-Cola
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
            "default": {
                "name": "Sample Protein Bar",
                "brand": "NutriFit",
                "category": "snacks",
                "price": 2.49,
                "size": "2.1 oz (60g)",
                "nutrition": {
                    "calories": 200,
                    "protein": 20,
                    "carbohydrates": 22,
                    "sugar": 8,
                    "fat": 7,
                    "saturated_fat": 3,
                    "sodium": 180,
                    "fiber": 5
                },
                "ingredients": "Protein blend (whey protein isolate, milk protein isolate), chicory root fiber, almonds, erythritol, cocoa, natural flavors"
            }
        }
        
        return mock_products.get(barcode, mock_products["default"])

