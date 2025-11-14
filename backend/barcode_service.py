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


def clean_category(category_tag: str) -> str:
    """
    Clean Open Food Facts category tags to user-friendly names.

    Args:
        category_tag: Raw category tag (e.g., "en:plant-based-foods-and-beverages")

    Returns:
        Clean category name (e.g., "Food & Beverages")
    """
    if not category_tag:
        return "Food"

    # Remove language prefix (e.g., "en:", "fr:")
    cleaned = category_tag.split(':')[-1]

    # Replace dashes and underscores with spaces
    cleaned = cleaned.replace('-', ' ').replace('_', ' ')

    # Capitalize each word
    cleaned = ' '.join(word.capitalize() for word in cleaned.split())

    # Simplify common categories
    if 'plant based' in cleaned.lower() or 'beverages' in cleaned.lower():
        return "Food & Beverages"
    elif 'snack' in cleaned.lower():
        return "Snacks"
    elif 'dairy' in cleaned.lower() or 'milk' in cleaned.lower():
        return "Dairy"
    elif 'meat' in cleaned.lower():
        return "Meat & Protein"
    elif 'fruit' in cleaned.lower() or 'vegetable' in cleaned.lower():
        return "Produce"

    # Return simplified version or just "Food" if too technical
    if len(cleaned) > 25:
        return "Food"

    return cleaned


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

        # Extract nutrition values with defaults
        def get_nutrient(key_100g, key_regular, default=0):
            """Helper to get nutrient value with fallback"""
            value = nutriments.get(key_100g) or nutriments.get(key_regular)
            return value if value is not None else default

        # Get and clean category
        raw_category = product.get('categories_tags', ['Food'])[0] if product.get('categories_tags') else 'Food'
        category = clean_category(raw_category)

        nutrition = {
            'name': product_name,
            'category': category,
            'brands': brands,
            'image_url': product.get('image_url', ''),
            'nutrition': {
                'serving_size': serving_size or '100g',
                'servings_per_container': servings_per_container if servings_per_container is not None else 1,
                'calories': get_nutrient('energy-kcal_100g', 'energy-kcal', 0),
                'protein': get_nutrient('proteins_100g', 'proteins', 0),
                'carbs_total': get_nutrient('carbohydrates_100g', 'carbohydrates', 0),
                'sugar_total': get_nutrient('sugars_100g', 'sugars', 0),
                'fat_total': get_nutrient('fat_100g', 'fat', 0),
                'saturated_fat': get_nutrient('saturated-fat_100g', 'saturated-fat', 0),
                'trans_fat': get_nutrient('trans-fat_100g', 'trans-fat', 0),
                'cholesterol': get_nutrient('cholesterol_100g', 'cholesterol', 0),
                'sodium': get_nutrient('sodium_100g', 'sodium', 0),
                'dietary_fiber': get_nutrient('fiber_100g', 'fiber', 0),
            }
        }

        # Convert sodium from g to mg if needed (only if non-zero)
        sodium_val = nutrition['nutrition'].get('sodium', 0)
        if sodium_val > 0 and sodium_val < 10:
            # Likely in grams, convert to mg
            nutrition['nutrition']['sodium'] = sodium_val * 1000

        # Ensure all values are numeric (convert to float)
        for key, value in nutrition['nutrition'].items():
            if key != 'serving_size':  # Skip serving_size as it's a string
                try:
                    nutrition['nutrition'][key] = float(value) if value is not None else 0.0
                except (ValueError, TypeError):
                    nutrition['nutrition'][key] = 0.0

        return nutrition

    except Exception as e:
        logger.error(f"Error extracting nutrition data: {e}", exc_info=True)
        return None


def search_products(query: str, limit: int = 10) -> list[Dict[str, Any]]:
    """
    Search for products by name in Open Food Facts database.
    Prioritizes US/English products.

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

        # Search API endpoint with country filter for US products
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            'search_terms': query,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            'page_size': limit * 3,  # Request more to filter for English products
            'tagtype_0': 'countries',
            'tag_contains_0': 'contains',
            'tag_0': 'united-states',  # Prioritize US products
            'sort_by': 'unique_scans_n',  # Sort by popularity
        }

        logger.info(f"Searching US products for: {query}")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            logger.warning(f"Product search failed with status {response.status_code}")
            return []

        data = response.json()
        products = data.get('products', [])

        # If no US products found, try global search with English filter
        if not products or len(products) < 3:
            logger.info(f"Few US products found, trying global search")
            params_global = {
                'search_terms': query,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': limit * 3,
                'sort_by': 'unique_scans_n',
            }
            response = requests.get(url, params=params_global, timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])

        # Filter and extract nutrition data from each product
        results = []
        for product in products:
            if len(results) >= limit:
                break

            # Filter for English products
            product_name = product.get('product_name') or product.get('product_name_en', '')

            # Skip products without English names or with non-Latin characters
            if not product_name:
                continue

            # Check if product name is mostly English (has ASCII characters)
            try:
                ascii_ratio = sum(ord(c) < 128 for c in product_name) / len(product_name)
                if ascii_ratio < 0.7:  # Skip if less than 70% ASCII
                    logger.debug(f"Skipping non-English product: {product_name}")
                    continue
            except:
                continue

            nutrition_data = extract_nutrition_from_product(product)
            if nutrition_data:
                # Add barcode for reference
                nutrition_data['barcode'] = product.get('code', '')
                results.append(nutrition_data)

        logger.info(f"Found {len(results)} English products for query: {query}")
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
