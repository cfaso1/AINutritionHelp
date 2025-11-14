#!/usr/bin/env python3
"""
REST API for AI Nutrition Help - Production Version
With proper authentication, security, and error handling
"""

import logging
import sys
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime
from pathlib import Path
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration
from config.config import active_config as Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Reduce werkzeug logging noise in production
if not Config.FLASK_DEBUG:
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Import backend modules
from backend.database import (
    init_database,
    create_user,
    authenticate_user,
    update_user_profile,
    get_user_profile,
    add_weight_entry,
    get_weight_history,
    calculate_bmi,
    migrate_database
)

# Import authentication
from backend.auth import AuthManager, get_current_user_id

# Barcode Service
try:
    from backend.barcode_service import lookup_barcode, search_products
    USE_BARCODE_SERVICE = True
except ImportError as e:
    logger.warning(f"Barcode service not available: {e}")
    USE_BARCODE_SERVICE = False

# Nutrition Agent Service
try:
    from backend.nutrition_agent_service import get_nutrition_agent_service, run_async
    USE_NUTRITION_AGENT = True
except ImportError as e:
    logger.warning(f"Nutrition Agent not available: {e}")
    USE_NUTRITION_AGENT = False

# OCR Ingestion Pipeline
try:
    from backend.ingest import (
        extract_text_from_image,
        parse_nutrition_text,
        needs_clarification,
        get_clarification_form_data,
        merge_user_corrections,
        validate_nutrition_data
    )
    USE_OCR = True
except ImportError as e:
    logger.warning(f"OCR pipeline not available: {e}")
    USE_OCR = False

# Validate configuration
try:
    Config.validate()
    logger.info(f"Configuration validated successfully (env: {Config.FLASK_ENV})")
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# CORS - Use whitelist from config
CORS(app,
     origins=Config.ALLOWED_ORIGINS,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'])

# Rate Limiting
if Config.RATE_LIMIT_ENABLED:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[f"{Config.RATE_LIMIT_PER_MINUTE}/minute"],
        storage_uri="memory://"
    )
    logger.info("Rate limiting enabled")
else:
    # Dummy limiter that does nothing
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    limiter = DummyLimiter()

# Configuration
UPLOAD_FOLDER = Path(Config.UPLOAD_FOLDER)
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)

# Initialize Authentication Manager
auth_manager = AuthManager(Config.SECRET_KEY)

# Initialize database and run migrations
init_database()
migrate_database()
logger.info("Database initialized and migrations completed")


# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    if Config.FLASK_ENV == 'production':
        response.headers['Content-Security-Policy'] = "default-src 'self'"

    return response


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}", exc_info=True)

    if Config.FLASK_DEBUG:
        return jsonify({'error': 'Internal server error', 'details': str(error)}), 500
    else:
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {error}", exc_info=True)

    if Config.FLASK_DEBUG:
        return jsonify({
            'error': 'Unexpected error occurred',
            'details': str(error),
            'traceback': traceback.format_exc()
        }), 500
    else:
        return jsonify({'error': 'Unexpected error occurred'}), 500


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5/hour")  # Stricter limit for registration
def register():
    """Register a new user"""
    data = request.get_json()

    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields: username, email, password'}), 400

    # Validate password strength
    password = data['password']
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400

    user_id = create_user(data['username'], data['email'], password)

    if user_id:
        # Generate JWT token
        token = auth_manager.generate_token(user_id, data['username'], data['email'])

        logger.info(f"New user registered: {data['username']} (ID: {user_id})")

        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': data['username'],
            'email': data['email'],
            'token': token,
            'message': 'User registered successfully'
        }), 201
    else:
        return jsonify({'error': 'Username or email already exists'}), 400


@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10/hour")  # Limit login attempts
def login():
    """Login a user and return JWT token"""
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    user = authenticate_user(data['username'], data['password'])

    if user:
        # Generate JWT token
        token = auth_manager.generate_token(
            user['user_id'],
            user['username'],
            user['email']
        )

        logger.info(f"User logged in: {user['username']} (ID: {user['user_id']})")

        return jsonify({
            'success': True,
            'user': user,
            'token': token,
            'message': 'Login successful'
        }), 200
    else:
        logger.warning(f"Failed login attempt for username: {data['username']}")
        return jsonify({'error': 'Invalid username or password'}), 401


# ============================================================================
# PROFILE ENDPOINTS (AUTHENTICATED)
# ============================================================================

@app.route('/api/profile', methods=['GET'])
@auth_manager.require_auth
def get_profile():
    """Get authenticated user's profile"""
    user_id = get_current_user_id()
    profile = get_user_profile(user_id)

    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    return jsonify({
        'success': True,
        'profile': profile
    }), 200


@app.route('/api/profile', methods=['PUT', 'POST'])
@auth_manager.require_auth
def update_profile():
    """Update authenticated user's profile - stores in imperial units"""
    user_id = get_current_user_id()
    data = request.get_json() or {}
    logger.debug(f"Profile update for user {user_id}: {data}")

    import re

    # Validate and parse height in feet'inches format
    if 'height' in data:
        height_str = str(data['height']).strip()

        if not re.match(r"^\d+'\d+\"?$", height_str):
            return jsonify({
                'error': "Height must be in format feet'inches (e.g., 5'8). Use only an apostrophe (')."
            }), 400

        try:
            height_str = height_str.rstrip('"')
            feet, inches = height_str.split("'")
            feet = int(feet)
            inches = int(inches)

            if not (3 <= feet <= 8):
                return jsonify({'error': 'Height feet must be between 3 and 8'}), 400
            if not (0 <= inches <= 11):
                return jsonify({'error': 'Height inches must be between 0 and 11'}), 400

            data['height_feet'] = feet
            data['height_inches'] = inches
            data['height_display'] = f"{feet}'{inches}\""
            data.pop('height')

        except Exception as e:
            logger.error(f"Height parse failed: {e}")
            return jsonify({
                'error': "Invalid height format. Use feet'inches (e.g., 5'8)"
            }), 400

    # Handle weight in pounds
    if 'weight' in data or 'weight_lbs' in data or 'current_weight_lbs' in data:
        weight_lbs = data.get('weight') or data.get('weight_lbs') or data.get('current_weight_lbs')

        try:
            weight_lbs = float(weight_lbs)

            if not (66 <= weight_lbs <= 660):
                return jsonify({
                    'error': 'Weight must be between 66 and 660 pounds'
                }), 400

            data['weight_lbs'] = round(weight_lbs, 1)
            data.pop('weight', None)
            data.pop('current_weight_lbs', None)

        except (ValueError, TypeError) as e:
            logger.error(f"Weight parse failed: {e}")
            return jsonify({
                'error': 'Weight must be a valid number in pounds'
            }), 400

    # Calculate BMI if we have both height and weight
    profile = get_user_profile(user_id)
    height_feet = data.get('height_feet') or (profile.get('height_feet') if profile else None)
    height_inches = data.get('height_inches') or (profile.get('height_inches') if profile else None)
    weight_lbs = data.get('weight_lbs') or (profile.get('weight_lbs') if profile else None)

    if height_feet and height_inches is not None and weight_lbs:
        total_height_inches = (height_feet * 12) + height_inches
        bmi = (weight_lbs / (total_height_inches ** 2)) * 703
        data['bmi'] = round(bmi, 1)

        # Convert to metric for AI usage
        height_cm = total_height_inches * 2.54
        current_weight_kg = weight_lbs * 0.453592
        data['height_cm'] = round(height_cm, 1)
        data['current_weight_kg'] = round(current_weight_kg, 1)

    # Ensure numeric fields are proper types
    numeric_fields = [
        'height_feet', 'height_inches', 'weight_lbs', 'bmi',
        'daily_calorie_target', 'daily_protein_target_g',
        'daily_carbs_target_g', 'daily_fat_target_g'
    ]

    for field in numeric_fields:
        if field in data:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError) as e:
                logger.error(f'Type conversion error for {field}: {e}')
                return jsonify({
                    'error': f'{field} must be a valid number'
                }), 400

    # Save profile to database
    success = update_user_profile(user_id, data)

    if success:
        profile = get_user_profile(user_id)

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': profile
        }), 200
    else:
        logger.error(f"Failed to update profile for user {user_id}")
        return jsonify({
            'error': 'Failed to update profile in database'
        }), 400


@app.route('/api/profile/setup', methods=['POST'])
@auth_manager.require_auth
def initial_profile_setup():
    """Initial profile setup - for first-time user onboarding"""
    user_id = get_current_user_id()
    data = request.get_json() or {}

    import re

    # Validate and parse height
    if 'height' not in data:
        return jsonify({'error': 'Height is required'}), 400

    height_str = str(data['height']).strip()
    if not re.match(r"^\d+'\d+\"?$", height_str):
        return jsonify({'error': "Height must be in format feet'inches (e.g., 5'8)"}), 400

    try:
        height_str = height_str.rstrip('"')
        feet, inches = height_str.split("'")
        feet, inches = int(feet), int(inches)

        if not (3 <= feet <= 8) or not (0 <= inches <= 11):
            return jsonify({'error': 'Invalid height range'}), 400

        data['height_feet'] = feet
        data['height_inches'] = inches
        data['height_display'] = f"{feet}'{inches}\""
        data.pop('height')

    except Exception as e:
        logger.error(f"Height parse error: {e}")
        return jsonify({'error': 'Invalid height format'}), 400

    # Validate and parse weight
    weight_key = 'current_weight_lbs' if 'current_weight_lbs' in data else 'weight'
    if weight_key not in data:
        return jsonify({'error': 'Weight is required'}), 400

    try:
        weight_lbs = float(data[weight_key])
        if not (66 <= weight_lbs <= 660):
            return jsonify({'error': 'Weight must be between 66 and 660 pounds'}), 400

        data['weight_lbs'] = round(weight_lbs, 1)
        data.pop(weight_key, None)
        data.pop('weight', None)

    except (ValueError, TypeError):
        return jsonify({'error': 'Weight must be a valid number'}), 400

    # Calculate BMI
    total_height_inches = (data['height_feet'] * 12) + data['height_inches']
    bmi = (data['weight_lbs'] / (total_height_inches ** 2)) * 703
    data['bmi'] = round(bmi, 1)

    # Convert to metric for AI usage
    height_cm = total_height_inches * 2.54
    current_weight_kg = data['weight_lbs'] * 0.453592
    data['height_cm'] = round(height_cm, 1)
    data['current_weight_kg'] = round(current_weight_kg, 1)

    # Save to database
    success = update_user_profile(user_id, data)

    if success:
        profile = get_user_profile(user_id)
        logger.info(f"Initial profile setup completed for user {user_id}")
        return jsonify({
            'success': True,
            'message': 'Profile created successfully',
            'profile': profile
        }), 201
    else:
        return jsonify({'error': 'Failed to save profile'}), 500


# ============================================================================
# NUTRITION INGESTION - BARCODE, OCR & MANUAL ENTRY (AUTHENTICATED)
# ============================================================================

@app.route('/api/nutrition/barcode/<barcode>', methods=['GET'])
@auth_manager.require_auth
def nutrition_barcode(barcode):
    """Look up nutrition facts by barcode using Open Food Facts"""
    if not USE_BARCODE_SERVICE:
        return jsonify({'error': 'Barcode service not available'}), 503

    try:
        logger.info(f"Barcode lookup requested: {barcode} by user {get_current_user_id()}")

        product_data = lookup_barcode(barcode)

        if not product_data:
            return jsonify({
                'success': False,
                'error': 'Product not found in database',
                'message': 'This barcode was not found. Please try manual entry or search by product name.'
            }), 404

        logger.info(f"Barcode lookup successful: {product_data.get('name', 'Unknown')}")

        return jsonify({
            'success': True,
            'product': product_data,
            'source': 'Open Food Facts'
        }), 200

    except Exception as e:
        logger.error(f"Barcode lookup failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Barcode lookup failed',
            'message': 'Unable to look up product. Please try again or use manual entry.'
        }), 500


@app.route('/api/nutrition/search', methods=['GET'])
@auth_manager.require_auth
def nutrition_search():
    """Search for products by name"""
    if not USE_BARCODE_SERVICE:
        return jsonify({'error': 'Search service not available'}), 503

    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify({'error': 'Search query must be at least 2 characters'}), 400

    try:
        logger.info(f"Product search requested: '{query}' by user {get_current_user_id()}")

        results = search_products(query, limit=10)

        logger.info(f"Search returned {len(results)} results for '{query}'")

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'query': query
        }), 200

    except Exception as e:
        logger.error(f"Product search failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'message': 'Unable to search products. Please try again.'
        }), 500


@app.route('/api/nutrition/ocr', methods=['POST'])
@auth_manager.require_auth
def nutrition_ocr():
    """Extract nutrition facts from uploaded image using OCR"""
    if not USE_OCR:
        return jsonify({'error': 'OCR service not available. Install required dependencies.'}), 503

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(Config.ALLOWED_EXTENSIONS)}'
        }), 400

    try:
        image_bytes = file.read()

        # Validate file size
        if len(image_bytes) > Config.MAX_CONTENT_LENGTH:
            return jsonify({'error': f'File too large. Max size: {Config.MAX_UPLOAD_SIZE_MB}MB'}), 400

        # Extract text using OCR
        logger.info(f"Extracting text from nutrition label for user {get_current_user_id()}")
        ocr_text = extract_text_from_image(image_bytes)

        if not ocr_text or len(ocr_text.strip()) < 10:
            return jsonify({
                'success': False,
                'error': 'Could not extract text from image. Please try manual entry.',
                'needs_manual_entry': True
            }), 200

        # Parse nutrition data from text
        parse_result = parse_nutrition_text(ocr_text)
        nutrition_data = parse_result['data']
        confidences = parse_result['confidences']

        # Check if clarification needed
        clarification_info = needs_clarification(nutrition_data, confidences)

        if clarification_info['needs_clarification']:
            missing_count = len(clarification_info['missing_fields'])
            if missing_count >= 7:
                return jsonify({
                    'success': False,
                    'error': 'Could not extract nutrition data from image. Please use manual entry.',
                    'needs_manual_entry': True
                }), 200

            form_data = get_clarification_form_data(nutrition_data, confidences)

            return jsonify({
                'success': True,
                'needs_clarification': True,
                'data': nutrition_data,
                'confidences': confidences,
                'clarification_fields': form_data,
                'message': clarification_info['prompt_message']
            }), 200
        else:
            return jsonify({
                'success': True,
                'needs_clarification': False,
                'data': nutrition_data,
                'confidences': confidences,
                'message': 'Nutrition facts extracted successfully'
            }), 200

    except Exception as e:
        logger.error(f"OCR processing failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'OCR processing failed',
            'needs_manual_entry': True
        }), 200


@app.route('/api/nutrition/manual', methods=['POST'])
@auth_manager.require_auth
def nutrition_manual():
    """Accept manually entered nutrition facts"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        validation_result = validate_nutrition_data(data)

        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'validation_errors': validation_result['errors']
            }), 400

        return jsonify({
            'success': True,
            'data': data,
            'message': 'Manual nutrition data validated successfully'
        }), 200

    except Exception as e:
        logger.error(f"Manual entry validation failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Validation failed'
        }), 500


@app.route('/api/nutrition/clarify', methods=['POST'])
@auth_manager.require_auth
def nutrition_clarify():
    """Accept user corrections/clarifications and merge with original data"""
    data = request.get_json()

    if not data or 'original_data' not in data or 'corrections' not in data:
        return jsonify({'error': 'Missing original_data or corrections'}), 400

    try:
        original_data = data['original_data']
        corrections = data['corrections']

        merged_data = merge_user_corrections(original_data, corrections)
        validation_result = validate_nutrition_data(merged_data)

        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Validation failed after corrections',
                'validation_errors': validation_result['errors']
            }), 400

        return jsonify({
            'success': True,
            'data': merged_data,
            'message': 'Corrections applied successfully'
        }), 200

    except Exception as e:
        logger.error(f"Clarification merge failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to apply corrections'
        }), 500


# ============================================================================
# NUTRITION EVALUATION (AUTHENTICATED)
# ============================================================================

def clean_nutrition_data(nutrition_dict):
    """
    Clean and normalize nutrition data to ensure all values are floats
    and keys match what the AI agent expects.
    """
    if not nutrition_dict:
        return nutrition_dict

    # Mapping from OCR parser keys to AI agent keys
    KEY_MAPPING = {
        'carbs_total': 'carbohydrates',  # OCR uses carbs_total, AI expects carbohydrates
        'sugar_total': 'sugar',          # OCR uses sugar_total, AI expects sugar
        'fat_total': 'fat',              # OCR uses fat_total, AI expects fat
        'dietary_fiber': 'fiber',        # OCR uses dietary_fiber, AI expects fiber
    }

    # Required nutrition fields with defaults
    REQUIRED_FIELDS = {
        'calories': 0.0,
        'protein': 0.0,
        'carbohydrates': 0.0,
        'sugar': 0.0,
        'fat': 0.0,
        'saturated_fat': 0.0,
        'trans_fat': 0.0,
        'cholesterol': 0.0,
        'sodium': 0.0,
        'fiber': 0.0,
        'serving_size': 100.0,
        'servings_per_container': 1.0
    }

    cleaned = {}
    import re

    for key, value in nutrition_dict.items():
        # Map key to AI-expected name
        normalized_key = KEY_MAPPING.get(key, key)

        if normalized_key == 'serving_size':
            if value is None:
                cleaned[normalized_key] = 100.0
            elif isinstance(value, str):
                match = re.search(r'(\d+(?:\.\d+)?)', str(value))
                if match:
                    cleaned[normalized_key] = float(match.group(1))
                else:
                    cleaned[normalized_key] = 100.0
            else:
                try:
                    cleaned[normalized_key] = float(value)
                except (ValueError, TypeError):
                    cleaned[normalized_key] = 100.0
        else:
            if value is None:
                # Use 0 for missing values
                cleaned[normalized_key] = 0.0
            else:
                try:
                    cleaned[normalized_key] = float(value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {key}={value} to float, using 0")
                    cleaned[normalized_key] = 0.0

    # Ensure all required fields are present
    for field, default_value in REQUIRED_FIELDS.items():
        if field not in cleaned:
            cleaned[field] = default_value
            logger.debug(f"Added missing field {field} with default {default_value}")

    return cleaned


def calculate_unit_price(product_data):
    """Calculate unit price (price per serving)"""
    if 'price' not in product_data or not product_data['price']:
        return product_data

    if 'nutrition' not in product_data or not product_data['nutrition']:
        return product_data

    servings = product_data['nutrition'].get('servings_per_container')

    if servings and servings > 0:
        unit_price = product_data['price'] / servings
        product_data['unit_price'] = round(unit_price, 2)
    else:
        product_data['unit_price'] = product_data['price']

    return product_data


@app.route('/api/agent/evaluate', methods=['POST'])
@auth_manager.require_auth
def evaluate_with_agent():
    """Comprehensive evaluation using nutrition agent"""
    if not USE_NUTRITION_AGENT:
        return jsonify({'error': 'Nutrition agent not available. Check API keys.'}), 503

    data = request.get_json()
    user_id = get_current_user_id()

    if not data or 'product' not in data:
        return jsonify({'error': 'Missing product data'}), 400

    product_data = data['product'].copy()

    # Clean nutrition data
    if 'nutrition' in product_data and product_data['nutrition']:
        product_data['nutrition'] = clean_nutrition_data(product_data['nutrition'])
        logger.info(f"Cleaned nutrition data keys: {list(product_data['nutrition'].keys())}")
        logger.info(f"Nutrition values: {product_data['nutrition']}")

    # Calculate unit price
    product_data = calculate_unit_price(product_data)

    # Get user profile for personalized evaluation
    profile = get_user_profile(user_id)

    if not profile:
        return jsonify({'error': 'User profile not found. Please complete your profile first.'}), 404

    try:
        agent_service = get_nutrition_agent_service()
        logger.info(f"Starting product evaluation for user {user_id}")

        evaluation = run_async(agent_service.evaluate_product(product_data, profile))
        logger.info(f"Product evaluation completed for user {user_id}")

        return jsonify({
            'success': True,
            'evaluation': evaluation
        }), 200

    except Exception as e:
        logger.error(f"Evaluation error for user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Evaluation failed'}), 500


@app.route('/api/agent/chat', methods=['POST'])
@auth_manager.require_auth
def chat_with_agent():
    """Chat with the AI nutrition companion"""
    if not USE_NUTRITION_AGENT:
        return jsonify({'error': 'Nutrition agent not available. Check API keys.'}), 503

    data = request.get_json()
    user_id = get_current_user_id()

    if not data or 'message' not in data:
        return jsonify({'error': 'Missing message field'}), 400

    message = data['message'].strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Get user profile for context
    profile = get_user_profile(user_id)

    try:
        context = {}

        if profile:
            context['user_profile'] = profile

        if 'product' in data:
            context['recent_product'] = data['product']

        if 'context' in data:
            context.update(data['context'])

        agent_service = get_nutrition_agent_service()
        response = run_async(agent_service.chat(message, context if context else None))

        return jsonify({
            'success': True,
            'message': response
        }), 200

    except Exception as e:
        logger.error(f"Chat error for user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Chat failed'}), 500


# ============================================================================
# WEIGHT TRACKING (AUTHENTICATED)
# ============================================================================

@app.route('/api/weight', methods=['POST'])
@auth_manager.require_auth
def add_weight():
    """Add a weight tracking entry"""
    data = request.get_json()
    user_id = get_current_user_id()

    if not data or 'weight_kg' not in data:
        return jsonify({'error': 'Missing weight_kg'}), 400

    weight_id = add_weight_entry(
        user_id=user_id,
        weight_kg=data['weight_kg'],
        notes=data.get('notes')
    )

    if weight_id:
        return jsonify({
            'success': True,
            'weight_id': weight_id,
            'message': 'Weight logged successfully'
        }), 201
    else:
        return jsonify({'error': 'Failed to log weight'}), 500


@app.route('/api/weight/history', methods=['GET'])
@auth_manager.require_auth
def get_weight():
    """Get weight history for authenticated user"""
    user_id = get_current_user_id()
    limit = request.args.get('limit', 30, type=int)
    history = get_weight_history(user_id, limit)

    # Calculate trend
    trend = "stable"
    if len(history) >= 2:
        recent_avg = sum(h['weight_kg'] for h in history[:3]) / min(3, len(history))
        older_avg = sum(h['weight_kg'] for h in history[-3:]) / min(3, len(history))
        if recent_avg > older_avg + 0.5:
            trend = "increasing"
        elif recent_avg < older_avg - 0.5:
            trend = "decreasing"

    current_weight = history[0]['weight_kg'] if history else None

    return jsonify({
        'success': True,
        'history': history,
        'current_weight_kg': current_weight,
        'trend': trend
    }), 200


# ============================================================================
# HEALTH CHECK & INFO
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint with service status"""
    # Check Tesseract OCR availability
    tesseract_available = False
    tesseract_version = None
    if USE_OCR:
        try:
            import pytesseract
            tesseract_version = pytesseract.get_tesseract_version()
            tesseract_available = True
        except Exception as e:
            logger.warning(f"Tesseract check failed: {e}")

    return jsonify({
        'status': 'healthy',
        'service': 'AI Nutrition Help API',
        'version': '2.0.0',
        'environment': Config.FLASK_ENV,
        'features': {
            'ocr_available': USE_OCR,
            'tesseract_available': tesseract_available,
            'tesseract_version': str(tesseract_version) if tesseract_version else None,
            'ai_agent_available': USE_NUTRITION_AGENT
        },
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    return jsonify({
        'message': 'AI Nutrition Help API - Production Version',
        'version': '2.0.0',
        'environment': Config.FLASK_ENV,
        'authentication': 'JWT Bearer Token Required',
        'endpoints': {
            'auth': ['POST /api/auth/register', 'POST /api/auth/login'],
            'profile': ['GET /api/profile', 'PUT /api/profile', 'POST /api/profile/setup'],
            'nutrition': [
                'POST /api/nutrition/ocr',
                'POST /api/nutrition/manual',
                'POST /api/nutrition/clarify'
            ],
            'evaluation': ['POST /api/agent/evaluate', 'POST /api/agent/chat'],
            'weight': ['POST /api/weight', 'GET /api/weight/history'],
            'health': ['GET /api/health']
        },
        'docs': 'See README.md for complete API documentation'
    }), 200


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n" + "="*60)
        print("  🍎 AI Nutrition Help API - Production Ready")
        print("="*60)
        print(f"  Environment: {Config.FLASK_ENV}")
        print(f"  Server: http://{Config.HOST}:{Config.PORT}")
        print(f"  Debug Mode: {'ON' if Config.FLASK_DEBUG else 'OFF'}")
        print(f"  Rate Limiting: {'ON' if Config.RATE_LIMIT_ENABLED else 'OFF'}")
        print(f"  CORS Origins: {', '.join(Config.ALLOWED_ORIGINS)}")
        print("="*60 + "\n")

    app.run(
        debug=Config.FLASK_DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
