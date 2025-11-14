"""
Barcode lookup service using Open Food Facts API
Free, crowdsourced nutrition database with 2.5M+ products
"""

import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Open Food Facts API endpoint
OPENFOODFACTS_API = "https://world.openfoodfacts.org/api/v0/product"


def lookup_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    """
    Look up product by barcode in Open Food Facts database.

    Args:
        barcode: UPC/EAN barcode (numeric string)

    Returns:
        Dictionary with product data or None if not found
    """
    try:
        # Clean barcode (remove spaces, ensure numeric)
        barcode_clean = ''.join(filter(str.isdigit, barcode))

        if not barcode_clean or len(barcode_clean) < 8:
            logger.warning(f"Invalid barcode format: {barcode}")
            return None

        # Query Open Food Facts API
        url = f"{OPENFOODFACTS_API}/{barcode_clean}.json"
        logger.info(f"Looking up barcode: {barcode_clean}")

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            logger.warning(f"Barcode lookup failed with status {response.status_code}")
            return None

        data = response.json()

        # Check if product was found
        if data.get('status') != 1 or 'product' not in data:
            logger.info(f"Barcode {barcode_clean} not found in database")
            return None

        product = data['product']

        # Extract nutrition data
        nutrition_data = extract_nutrition_from_product(product)

        if not nutrition_data:
            logger.warning(f"Product {barcode_clean} found but missing nutrition data")
            return None

        logger.info(f"Successfully found product: {nutrition_data.get('name', 'Unknown')}")
        return nutrition_data

    except requests.Timeout:
        logger.error(f"Timeout looking up barcode {barcode}")
        return None
    except requests.RequestException as e:
        logger.error(f"Request error looking up barcode {barcode}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error looking up barcode {barcode}: {e}", exc_info=True)
        return None


def extract_nutrition_from_product(product: Dict) -> Optional[Dict[str, Any]]:
    """
    Extract and normalize nutrition data from Open Food Facts product.

    Args:
        product: Product dictionary from API

    Returns:
        Normalized nutrition data dictionary
    """
    try:
        # Get nutriments (per 100g by default)
        nutriments = product.get('nutriments', {})

        # Check if we have basic nutrition data
        if not nutriments or 'energy-kcal_100g' not in nutriments:
            # Try getting serving size data
            nutriments_serving = product.get('nutriments', {})
            if 'energy-kcal_serving' not in nutriments_serving:
                return None

        # Extract basic info
        product_name = product.get('product_name') or product.get('product_name_en') or 'Unknown Product'
        brands = product.get('brands', '')
        if brands:
            product_name = f"{brands} - {product_name}"

        # Get serving size info
        serving_size = product.get('serving_size') or product.get('serving_quantity', '')
        servings_per_container = None

        # Try to calculate servings per container
        if serving_size and product.get('quantity'):
            try:
                # Parse quantity (e.g., "500g" -> 500)
                import re
                quantity_match = re.search(r'(\d+(?:\.\d+)?)', product.get('quantity', ''))
                serving_match = re.search(r'(\d+(?:\.\d+)?)', serving_size)

                if quantity_match and serving_match:
                    total_grams = float(quantity_match.group(1))
                    serving_grams = float(serving_match.group(1))
                    if serving_grams > 0:
                        servings_per_container = round(total_grams / serving_grams, 1)
            except:
                pass

        # Build nutrition data structure (normalized to per serving if available)
        # Open Food Facts provides data per 100g, we'll use that as "serving"
        nutrition = {
            'name': product_name,
            'category': product.get('categories_tags', ['Food'])[0] if product.get('categories_tags') else 'Food',
            'brands': brands,
            'image_url': product.get('image_url', ''),
            'nutrition': {
                'serving_size': serving_size or '100g',
                'servings_per_container': servings_per_container or 1,
                'calories': nutriments.get('energy-kcal_100g') or nutriments.get('energy-kcal'),
                'protein': nutriments.get('proteins_100g') or nutriments.get('proteins'),
                'carbs_total': nutriments.get('carbohydrates_100g') or nutriments.get('carbohydrates'),
                'sugar_total': nutriments.get('sugars_100g') or nutriments.get('sugars'),
                'fat_total': nutriments.get('fat_100g') or nutriments.get('fat'),
                'saturated_fat': nutriments.get('saturated-fat_100g') or nutriments.get('saturated-fat'),
                'trans_fat': nutriments.get('trans-fat_100g') or nutriments.get('trans-fat', 0),
                'cholesterol': nutriments.get('cholesterol_100g') or nutriments.get('cholesterol', 0),
                'sodium': nutriments.get('sodium_100g') or nutriments.get('sodium', 0),
                'dietary_fiber': nutriments.get('fiber_100g') or nutriments.get('fiber'),
            }
        }

        # Convert sodium from g to mg if needed
        if nutrition['nutrition'].get('sodium') and nutrition['nutrition']['sodium'] < 10:
            # Likely in grams, convert to mg
            nutrition['nutrition']['sodium'] *= 1000

        # Remove None values from nutrition
        nutrition['nutrition'] = {k: v for k, v in nutrition['nutrition'].items() if v is not None}

        return nutrition

    except Exception as e:
        logger.error(f"Error extracting nutrition data: {e}", exc_info=True)
        return None


def search_products(query: str, limit: int = 10) -> list[Dict[str, Any]]:
    """
    Search for products by name in Open Food Facts database.

    Args:
        query: Product name search query
        limit: Maximum number of results to return

    Returns:
        List of product dictionaries
    """
    try:
        if not query or len(query.strip()) < 2:
            logger.warning("Search query too short")
            return []

        # Search API endpoint
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            'search_terms': query,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            'page_size': limit
        }

        logger.info(f"Searching products for: {query}")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            logger.warning(f"Product search failed with status {response.status_code}")
            return []

        data = response.json()
        products = data.get('products', [])

        # Extract nutrition data from each product
        results = []
        for product in products[:limit]:
            nutrition_data = extract_nutrition_from_product(product)
            if nutrition_data:
                # Add barcode for reference
                nutrition_data['barcode'] = product.get('code', '')
                results.append(nutrition_data)

        logger.info(f"Found {len(results)} products for query: {query}")
        return results

    except requests.Timeout:
        logger.error(f"Timeout searching for products: {query}")
        return []
    except requests.RequestException as e:
        logger.error(f"Request error searching products: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error searching products: {e}", exc_info=True)
        return []
