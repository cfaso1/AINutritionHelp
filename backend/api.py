#!/usr/bin/env python3
"""
REST API for AI Nutrition Help - Hackathon Demo Version
NO AUTHENTICATION - For demo purposes only!

USAGE:
    python api.py

Then open frontend/index.html in your browser!
"""

import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reduce werkzeug logging noise
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
    migrate_database,
    migrate_to_imperial
)
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

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow all origins for demo

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize database and create a demo user
init_database()
migrate_database()  # Run migrations for price column
migrate_to_imperial()  # Run imperial unit migration

# Create a single demo user for the hackathon (user_id will always be 1)
DEMO_USER_ID = 1
try:
    # Try to create demo user, ignore if already exists
    user_id = create_user("demo_user", "demo@hackathon.com", "demo123")
    if user_id:
        # Set up a basic profile
        update_user_profile(DEMO_USER_ID, {
            'height_cm': 175,
            'current_weight_kg': 75,
            'goal_type': 'general_health',
            'activity_level': 'moderately_active',
            'diet_type': 'standard',
            'daily_calorie_target': 2000,
            'daily_protein_target_g': 100,
            'daily_carbs_target_g': 250,
            'daily_fat_target_g': 65
        })
        logger.info(f"Demo user created (ID: {DEMO_USER_ID})")
except:
    logger.info(f"Using existing demo user (ID: {DEMO_USER_ID})")




# ============================================================================
# AUTHENTICATION ENDPOINTS (DEMO)
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user (demo authentication)."""
    data = request.get_json()

    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields: username, email, password'}), 400

    user_id = create_user(data['username'], data['email'], data['password'])

    if user_id:
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'User registered successfully'
        }), 201
    else:
        return jsonify({'error': 'Username or email already exists'}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user (demo authentication)."""
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    user = authenticate_user(data['username'], data['password'])

    if user:
        return jsonify({
            'success': True,
            'user': user,
            'message': 'Login successful'
        }), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


# ============================================================================
# SIMPLIFIED ENDPOINTS - NO AUTH REQUIRED
# ============================================================================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get demo user's profile."""
    profile = get_user_profile(DEMO_USER_ID)
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    return jsonify({
        'success': True,
        'profile': profile
    }), 200

@app.route('/api/profile', methods=['PUT', 'POST'])
def update_profile():
    """Update demo user profile - stores in imperial units."""
    data = request.get_json() or {}
    logger.debug(f"/api/profile called with payload: {data}")

    import re

    # Validate and parse height in feet'inches format
    if 'height' in data:
        height_str = str(data['height']).strip()
        
        # Must be in format like 5'8 (only apostrophe allowed)
        if not re.match(r"^\d+'\d+\"?$", height_str):
            return jsonify({
                'error': "Height must be in format feet'inches (e.g., 5'8). Use only an apostrophe (')."
            }), 400
        
        try:
            # Remove trailing quote if present
            height_str = height_str.rstrip('"')
            feet, inches = height_str.split("'")
            feet = int(feet)
            inches = int(inches)
            
            # Validate ranges
            if not (3 <= feet <= 8):
                return jsonify({'error': 'Height feet must be between 3 and 8'}), 400
            if not (0 <= inches <= 11):
                return jsonify({'error': 'Height inches must be between 0 and 11'}), 400
            
            # Store as separate fields
            data['height_feet'] = feet
            data['height_inches'] = inches
            # Also store the formatted string for display
            data['height_display'] = f"{feet}'{inches}\""
            
            # Remove the original 'height' key
            data.pop('height')
            
            logger.debug(f"Parsed height: {feet}'{inches}\"")
            
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
            
            # Validate range (66-660 lbs is reasonable)
            if not (66 <= weight_lbs <= 660):
                return jsonify({
                    'error': 'Weight must be between 66 and 660 pounds'
                }), 400
            
            # Store as weight_lbs
            data['weight_lbs'] = round(weight_lbs, 1)
            
            # Remove other weight keys
            data.pop('weight', None)
            data.pop('current_weight_lbs', None)
            
            logger.debug(f"Parsed weight: {weight_lbs} lbs")
            
        except (ValueError, TypeError) as e:
            logger.error(f"Weight parse failed: {e}")
            return jsonify({
                'error': 'Weight must be a valid number in pounds'
            }), 400

    # Calculate BMI if we have both height and weight
    # Use existing values if new ones weren't provided
    profile = get_user_profile(DEMO_USER_ID)

    height_feet = data.get('height_feet') or (profile.get('height_feet') if profile else None)
    height_inches = data.get('height_inches') or (profile.get('height_inches') if profile else None)
    weight_lbs = data.get('weight_lbs') or (profile.get('weight_lbs') if profile else None)

    if height_feet and height_inches is not None and weight_lbs:
        # BMI formula: (weight_lbs / (height_inches^2)) * 703
        total_height_inches = (height_feet * 12) + height_inches
        bmi = (weight_lbs / (total_height_inches ** 2)) * 703
        data['bmi'] = round(bmi, 1)
        logger.debug(f"Calculated BMI: {bmi:.1f}")

        # Convert to metric for AI usage
        height_cm = total_height_inches * 2.54
        current_weight_kg = weight_lbs * 0.453592
        data['height_cm'] = round(height_cm, 1)
        data['current_weight_kg'] = round(current_weight_kg, 1)
        logger.debug(f"Converted to metric - height_cm: {height_cm:.1f}, weight_kg: {current_weight_kg:.1f}")

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

    # Debug output
    logger.debug(f'Data to save: {[(k, type(v).__name__, v) for k, v in data.items()]}')

    # Save profile to database
    success = update_user_profile(DEMO_USER_ID, data)
    logger.debug(f"update_user_profile returned: {success}")
    
    if success:
        # Retrieve updated profile
        profile = get_user_profile(DEMO_USER_ID)
        logger.debug(f"Retrieved profile after save: {profile}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': profile
        }), 200
    else:
        logger.error("Failed to update profile in database")
        return jsonify({
            'error': 'Failed to update profile in database'
        }), 400

# ============================================================================
# NUTRITION INGESTION - OCR & MANUAL ENTRY
# ============================================================================

@app.route('/api/nutrition/ocr', methods=['POST'])
def nutrition_ocr():
    """
    Extract nutrition facts from uploaded image using OCR.
    Returns parsed data with confidence scores and clarification needs.
    """
    if not USE_OCR:
        return jsonify({'error': 'OCR service not available. Install required dependencies.'}), 503

    # Check if image was uploaded
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        # Read image bytes
        image_bytes = file.read()

        # Step 1: Extract text using OCR
        logger.info("Extracting text from nutrition label image")
        ocr_text = extract_text_from_image(image_bytes)

        if not ocr_text or len(ocr_text.strip()) < 10:
            return jsonify({
                'success': False,
                'error': 'Could not extract text from image. Please try manual entry.',
                'needs_manual_entry': True
            }), 200

        # Step 2: Parse nutrition data from text
        logger.info("Parsing nutrition data from OCR text")
        parse_result = parse_nutrition_text(ocr_text)
        nutrition_data = parse_result['data']
        confidences = parse_result['confidences']

        # Step 3: Check if clarification needed
        clarification_info = needs_clarification(nutrition_data, confidences)

        if clarification_info['needs_clarification']:
            # If ALL priority fields are missing, OCR failed completely - suggest manual entry
            missing_count = len(clarification_info['missing_fields'])
            if missing_count >= 7:  # Most/all fields missing
                return jsonify({
                    'success': False,
                    'error': 'Could not extract nutrition data from image. Please use manual entry.',
                    'needs_manual_entry': True,
                    'ocr_text_length': len(ocr_text)
                }), 200

            # Return data with clarification form
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
            # Data is complete and confident
            return jsonify({
                'success': True,
                'needs_clarification': False,
                'data': nutrition_data,
                'confidences': confidences,
                'message': 'Nutrition facts extracted successfully'
            }), 200

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return jsonify({
            'success': False,
            'error': f'OCR processing failed: {str(e)}',
            'needs_manual_entry': True
        }), 200


@app.route('/api/nutrition/manual', methods=['POST'])
def nutrition_manual():
    """
    Accept manually entered nutrition facts.
    Validates data and returns structured nutrition object.
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        # Validate the nutrition data
        validation_result = validate_nutrition_data(data)

        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'validation_errors': validation_result['errors']
            }), 400

        # Data is valid
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Manual nutrition data validated successfully'
        }), 200

    except Exception as e:
        logger.error(f"Manual entry validation failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}'
        }), 500


@app.route('/api/nutrition/clarify', methods=['POST'])
def nutrition_clarify():
    """
    Accept user corrections/clarifications and merge with original data.
    """
    data = request.get_json()

    if not data or 'original_data' not in data or 'corrections' not in data:
        return jsonify({'error': 'Missing original_data or corrections'}), 400

    try:
        original_data = data['original_data']
        corrections = data['corrections']

        # Merge corrections with original data
        merged_data = merge_user_corrections(original_data, corrections)

        # Validate merged data
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
            'error': f'Failed to apply corrections: {str(e)}'
        }), 500


# ============================================================================
# NUTRITION EVALUATION
# ============================================================================

def clean_nutrition_data(nutrition_dict):
    """
    Clean nutrition data to ensure all values are floats (not strings).
    Handles serving_size which may contain units like "100g".
    """
    if not nutrition_dict:
        return nutrition_dict

    cleaned = {}
    import re

    for key, value in nutrition_dict.items():
        if value is None:
            continue

        # Handle serving_size specially - extract just the number
        if key == 'serving_size':
            if isinstance(value, str):
                # Extract first number from string like "100g" or "100.0g"
                match = re.search(r'(\d+(?:\.\d+)?)', str(value))
                if match:
                    cleaned[key] = float(match.group(1))
                else:
                    logger.warning(f"Could not parse serving_size: {value}")
                    cleaned[key] = 100.0  # Default fallback
            else:
                cleaned[key] = float(value)
        else:
            # All other values should be floats
            try:
                cleaned[key] = float(value)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert {key}={value} to float, skipping")
                continue

    return cleaned


def calculate_unit_price(product_data):
    """
    Calculate unit price (price per serving) from total price and servings per container.

    Args:
        product_data: Product dictionary with price and nutrition data

    Returns:
        Updated product_data with unit_price field
    """
    if 'price' not in product_data or not product_data['price']:
        return product_data

    if 'nutrition' not in product_data or not product_data['nutrition']:
        return product_data

    servings = product_data['nutrition'].get('servings_per_container')

    if servings and servings > 0:
        unit_price = product_data['price'] / servings
        product_data['unit_price'] = round(unit_price, 2)
        logger.debug(f"Calculated unit_price: ${unit_price:.2f} (${product_data['price']:.2f} / {servings} servings)")
    else:
        # If no servings data, assume 1 serving (unit_price = total price)
        product_data['unit_price'] = product_data['price']
        logger.debug(f"No servings data, unit_price = total price: ${product_data['price']:.2f}")

    return product_data


@app.route('/api/agent/evaluate', methods=['POST'])
def evaluate_with_agent():
    """
    NEW: Comprehensive evaluation using nutrition agent.
    Evaluates product using health, price, and fitness agents.
    """
    if not USE_NUTRITION_AGENT:
        return jsonify({'error': 'Nutrition agent not available. Check API keys.'}), 503

    data = request.get_json()

    if not data or 'product' not in data:
        return jsonify({'error': 'Missing product data'}), 400

    product_data = data['product'].copy()

    # Clean nutrition data to ensure all values are floats
    if 'nutrition' in product_data and product_data['nutrition']:
        product_data['nutrition'] = clean_nutrition_data(product_data['nutrition'])
        logger.debug(f"Cleaned nutrition data: {product_data['nutrition']}")

    # Calculate unit price (price per serving)
    product_data = calculate_unit_price(product_data)

    # Get user profile for personalized evaluation
    profile = get_user_profile(DEMO_USER_ID)

    if not profile:
        return jsonify({'error': 'User profile not found'}), 404

    try:
        # Get nutrition agent service
        agent_service = get_nutrition_agent_service()

        logger.info("Starting product evaluation with agent")
        # Run comprehensive evaluation
        evaluation = run_async(agent_service.evaluate_product(product_data, profile))
        logger.info("Product evaluation completed successfully")

        return jsonify({
            'success': True,
            'evaluation': evaluation
        }), 200

    except Exception as e:
        logger.error(f"Evaluation error: {e}", exc_info=True)
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500




@app.route('/api/weight', methods=['POST'])
def add_weight():
    """Add a weight tracking entry for demo user."""
    data = request.get_json()

    if not data or 'weight_kg' not in data:
        return jsonify({'error': 'Missing weight_kg'}), 400

    weight_id = add_weight_entry(
        user_id=DEMO_USER_ID,
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
def get_weight():
    """Get weight history for demo user."""
    limit = request.args.get('limit', 30, type=int)
    history = get_weight_history(DEMO_USER_ID, limit)

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


@app.route('/api/agent/chat', methods=['POST'])
def chat_with_agent():
    """
    Chat with the AI nutrition companion.
    Send a message and optionally include context (recent product, user goals).
    """
    if not USE_NUTRITION_AGENT:
        return jsonify({'error': 'Nutrition agent not available. Check API keys.'}), 503

    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Missing message field'}), 400

    message = data['message'].strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Get user profile for context
    profile = get_user_profile(DEMO_USER_ID)

    try:
        # Build context from request
        context = {}

        # Add user profile to context
        if profile:
            context['user_profile'] = profile

        # Add recent product if provided
        if 'product' in data:
            context['recent_product'] = data['product']

        # Add any custom context
        if 'context' in data:
            context.update(data['context'])

        # Get nutrition agent service
        agent_service = get_nutrition_agent_service()

        # Chat with agent
        response = run_async(agent_service.chat(message, context if context else None))

        return jsonify({
            'success': True,
            'message': response
        }), 200

    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Nutrition Help API (Demo Mode)',
        'version': '1.0.0-hackathon',
        'demo_user_id': DEMO_USER_ID,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint."""
    return jsonify({
        'message': 'AI Nutrition Help API - Hackathon Demo (No Auth Required)',
        'version': '1.0.0-demo',
        'note': 'All endpoints use demo user - no authentication needed',
        'endpoints': {
            'profile': ['GET /api/profile', 'PUT /api/profile'],
            'nutrition': ['POST /api/agent/evaluate', 'POST /api/agent/chat'],
            'weight': ['POST /api/weight', 'GET /api/weight/history']
        },
        'demo': 'Open demo.html in your browser to test!'
    }), 200

@app.route('/api/profile/setup', methods=['POST'])
def initial_profile_setup():
    """Initial profile setup - for first-time user onboarding."""
    data = request.get_json() or {}
    logger.debug(f"Initial profile setup called with: {data}")

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

    logger.debug(f"Saving initial profile: {data}")

    # Save to database
    success = update_user_profile(DEMO_USER_ID, data)
    
    if success:
        profile = get_user_profile(DEMO_USER_ID)
        return jsonify({
            'success': True,
            'message': 'Profile created successfully',
            'profile': profile
        }), 201
    else:
        return jsonify({'error': 'Failed to save profile'}), 500



if __name__ == '__main__':
    # Only show banner once (not in reloader child process)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n🍎 AI Nutrition Help API")
        print("=" * 50)
        print("Server: http://localhost:5000")
        print("Frontend: Open frontend/index.html in browser")
        print("Demo Login: demo_user / demo123")
        print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
