from typing import Optional
from models.product import Product
from services.barcode_api import BarcodeAPIService
import asyncio




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

      
_barcode_agent_instance = None

def get_barcode_agent():
    """Get or create singleton instance of BarcodeScannerAgent"""
    global _barcode_agent_instance
    if _barcode_agent_instance is None:
        from services.barcode_api import BarcodeAPIService
        _barcode_agent_instance = BarcodeScannerAgent(BarcodeAPIService())
    return _barcode_agent_instance


def scan_barcode(barcode: str) -> dict:
    """
    Scan a barcode and return product information.
    
    This tool looks up a product by its barcode number and returns comprehensive
    information including name, brand, category, price, nutritional facts, and ingredients.
    
    Args:
        barcode: The barcode number (UPC/EAN format) to scan
        
    Returns:
        Dictionary containing product information or error message
    """
    agent = get_barcode_agent()
    
    # Run the async function synchronously
    try:
        product = asyncio.run(agent.scan(barcode))
    except RuntimeError:
        # If event loop is already running, use run_coroutine_threadsafe
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                product = pool.submit(lambda: asyncio.run(agent.scan(barcode))).result()
        else:
            product = asyncio.run(agent.scan(barcode))
    
    if product is None:
        return {
            "success": False,
            "error": "Product not found for this barcode"
        }
    
    return {
        "success": True,
        "barcode": product.barcode,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "price": product.price,
        "size": product.size,
        "unit_price": product.unit_price,
        "nutrition": product.nutrition,
        "ingredients": product.ingredients
    }


__all__ = ['scan_barcode', 'BarcodeScannerAgent', 'get_barcode_agent']
