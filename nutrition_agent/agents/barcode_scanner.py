from typing import Optional
from models.product import Product
from services.barcode_api import BarcodeAPIService


class BarcodeScannerAgent:
    """Agent responsible for scanning barcodes and fetching product data"""
    
    def __init__(self, barcode_service: BarcodeAPIService):
        self.barcode_service = barcode_service
    
    async def scan(self, barcode: str) -> Optional[Product]:
        """
        Scan a barcode and return product information
        
        Args:
            barcode: The barcode number to scan
            
        Returns:
            Product object if found, None otherwise
        """
        try:
            # Fetch product data from API
            product_data = await self.barcode_service.lookup(barcode)
            
            if not product_data:
                return None
            
            # Parse and structure the data
            product = self._parse_product_data(barcode, product_data)
            return product
            
        except Exception as e:
            print(f"Error scanning barcode: {e}")
            return None
    
    def _parse_product_data(self, barcode: str, data: dict) -> Product:
        """Parse API response into Product model"""
        
        # Extract nutrition information if available
        nutrition = None
        if "nutrition" in data:
            nutrition = {
                "calories": data["nutrition"].get("calories", 0),
                "protein": data["nutrition"].get("protein", 0),
                "carbohydrates": data["nutrition"].get("carbohydrates", 0),
                "sugar": data["nutrition"].get("sugar", 0),
                "fat": data["nutrition"].get("fat", 0),
                "saturated_fat": data["nutrition"].get("saturated_fat", 0),
                "sodium": data["nutrition"].get("sodium", 0),
                "fiber": data["nutrition"].get("fiber", 0),
            }
        
        # Calculate unit price if available
        unit_price = None
        if data.get("price") and data.get("size"):
            try:
                # Simple unit price calculation
                unit_price = float(data["price"]) / float(data.get("size", 1))
            except:
                pass
        
        product = Product(
            barcode=barcode,
            name=data.get("name", "Unknown Product"),
            brand=data.get("brand", "Unknown Brand"),
            category=data.get("category", "Uncategorized"),
            price=float(data.get("price", 0)),
            size=data.get("size"),
            unit_price=unit_price,
            nutrition=nutrition,
            ingredients=data.get("ingredients")
        )
        
        return product