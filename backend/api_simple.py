#!/usr/bin/env python3
"""
SIMPLIFIED REST API for AI Nutrition Help - Hackathon Demo Version
NO AUTHENTICATION - For demo purposes only!

USAGE:
    python api_simple.py

Then open demo.html in your browser!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path

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
# DEPRECATED: Old OCR-based nutrition scanner
# from backend.nutrition_reader import extract_text_from_image, parse_nutrition_info
# NEW: Nutrition Agent Service (barcode-based)
try:
    from backend.nutrition_agent_service import get_nutrition_agent_service, run_async
    USE_NUTRITION_AGENT = True
except ImportError as e:
    print(f"Warning: Nutrition Agent not available: {e}")
    USE_NUTRITION_AGENT = False

# Barcode detection from images
try:
    from backend.barcode_detector import extract_barcode_from_bytes
    USE_BARCODE_DETECTOR = True
except ImportError as e:
    print(f"Warning: Barcode detector not available: {e}")
    USE_BARCODE_DETECTOR = False

# Optional: Import custom AI model (will use demo mode if not available)
try:
    from backend.ai_model import analyze_nutrition as ai_analyze
    USE_AI_MODEL = True
except ImportError:
    USE_AI_MODEL = False

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
        print(f"✓ Demo user created (ID: {DEMO_USER_ID})")
except:
    print(f"✓ Using existing demo user (ID: {DEMO_USER_ID})")


def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_demo_analysis(nutrition_data, profile):
    """
    Generate demo analysis output.
    REPLACE THIS FUNCTION with your custom AI model integration.

    Args:
        nutrition_data: Dict with nutrition facts from OCR
        profile: User profile dict with goals and preferences

    Returns:
        String with nutrition analysis
    """
    calories = nutrition_data.get('calories', {}).get('total', 'Unknown')
    protein = nutrition_data.get('macronutrients', {}).get('protein', {}).get('amount_g', 'Unknown')
    carbs = nutrition_data.get('macronutrients', {}).get('carbohydrates', {}).get('total_g', 'Unknown')
    fat = nutrition_data.get('macronutrients', {}).get('fat', {}).get('total_g', 'Unknown')
    sodium = nutrition_data.get('micronutrients', {}).get('sodium_mg', 'Unknown')

    return f"""🤖 AI Nutrition Analysis (Demo Mode)

1. OVERALL HEALTH ASSESSMENT: 7/10
   - Calories: {calories} kcal
   - Protein: {protein}g
   - Carbs: {carbs}g
   - Fat: {fat}g
   - Sodium: {sodium}mg

2. KEY NUTRITIONAL HIGHLIGHTS:
   - Protein: {protein}g (Your daily goal: {profile.get('daily_protein_target_g', 100)}g)
   - Calories: {calories} kcal (Your daily goal: {profile.get('daily_calorie_target', 2000)} kcal)

3. DIETARY COMPATIBILITY:
   - Your Goal: {profile.get('goal_type', 'general health').replace('_', ' ').title()}
   - Your Diet: {profile.get('diet_type', 'standard').title()}
   - This food appears compatible with your dietary preferences

4. WARNINGS/CONCERNS:
   - Check sodium content: {sodium}mg
   - Review serving size carefully
   - Monitor added sugars

5. RECOMMENDATIONS:
   - Fits your {profile.get('goal_type', 'general health').replace('_', ' ')} goals
   - Consider portion size relative to daily targets
   - Balance with other meals throughout the day

6. PORTION GUIDANCE:
   - Review serving size information from the label
   - Track in your daily nutrition log
   - Stay within your daily calorie target

📝 Note: This is demo output. Replace generate_demo_analysis() in api_simple.py
with your custom trained AI model to get personalized recommendations!"""


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
    print("[DEBUG] /api/profile called with payload:", data)

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
            
            print(f"[DEBUG] Parsed height: {feet}'{inches}\"")
            
        except Exception as e:
            print("[DEBUG] Height parse failed:", e)
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
            
            print(f"[DEBUG] Parsed weight: {weight_lbs} lbs")
            
        except (ValueError, TypeError) as e:
            print("[DEBUG] Weight parse failed:", e)
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
        print(f"[DEBUG] Calculated BMI: {bmi:.1f}")

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
                print(f'[DEBUG] Type conversion error for {field}:', e)
                return jsonify({
                    'error': f'{field} must be a valid number'
                }), 400

    # Debug output
    print('[DEBUG] Data to save:', {k: (type(v).__name__, v) for k, v in data.items()})

    # Save profile to database
    success = update_user_profile(DEMO_USER_ID, data)
    print(f"[DEBUG] update_user_profile returned: {success}")
    
    if success:
        # Retrieve updated profile
        profile = get_user_profile(DEMO_USER_ID)
        print(f"[DEBUG] Retrieved profile after save: {profile}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': profile
        }), 200
    else:
        print("[DEBUG] Failed to update profile in database")
        return jsonify({
            'error': 'Failed to update profile in database'
        }), 400

# ============================================================================
# NUTRITION SCANNING - NEW BARCODE-BASED SYSTEM
# ============================================================================

@app.route('/api/barcode/scan', methods=['POST'])
def scan_barcode():
    """
    Scan a barcode and return product information.
    NEW endpoint using the nutrition-agent barcode scanner.
    """
    if not USE_NUTRITION_AGENT:
        return jsonify({'error': 'Nutrition agent not available. Check API keys.'}), 503

    data = request.get_json()

    if not data or 'barcode' not in data:
        return jsonify({'error': 'Missing barcode number'}), 400

    barcode = str(data['barcode']).strip()

    if not barcode:
        return jsonify({'error': 'Invalid barcode'}), 400

    try:
        # Get nutrition agent service
        agent_service = get_nutrition_agent_service()

        # Scan barcode asynchronously
        product_data = run_async(agent_service.scan_barcode(barcode))

        if not product_data:
            return jsonify({
                'error': 'Product not found. Please check the barcode number.',
                'suggestion': 'Try one of these test barcodes: 012000161551 (Coca-Cola), 078000113464 (Gatorade), 722252601025 (Quest Bar), 016000275683 (Cheerios)'
            }), 404

        return jsonify({
            'success': True,
            'product': product_data,
            'message': 'Product scanned successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to scan barcode: {str(e)}'}), 500


@app.route('/api/barcode/image', methods=['POST'])
def scan_barcode_image():
    """
    Upload a barcode image and automatically extract the barcode number.
    Then retrieve product information using the extracted barcode.
    """
    if not USE_BARCODE_DETECTOR:
        return jsonify({'error': 'Barcode detector not available. Install pyzbar and opencv-python.'}), 503

    if not USE_NUTRITION_AGENT:
        return jsonify({'error': 'Nutrition agent not available. Check API keys.'}), 503

    # Check if image file is present
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP'}), 400

    try:
        # Read image bytes
        image_bytes = file.read()

        # Extract barcode from image
        barcode = extract_barcode_from_bytes(image_bytes)

        if not barcode:
            return jsonify({
                'error': 'No barcode detected in image',
                'suggestion': 'Make sure the barcode is clearly visible and well-lit'
            }), 404

        # Now scan the extracted barcode
        agent_service = get_nutrition_agent_service()
        product_data = run_async(agent_service.scan_barcode(barcode))

        if not product_data:
            return jsonify({
                'error': f'Barcode detected ({barcode}) but product not found in database',
                'barcode': barcode,
                'suggestion': 'Try one of these test barcodes: 012000161551 (Coca-Cola), 078000113464 (Gatorade), 722252601025 (Quest Bar), 016000275683 (Cheerios)'
            }), 404

        return jsonify({
            'success': True,
            'barcode': barcode,
            'product': product_data,
            'message': f'Barcode {barcode} detected and product found'
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500


@app.route('/api/scan', methods=['POST'])
def scan_nutrition_label():
    """
    DEPRECATED: Old OCR-based nutrition label scanner.
    Kept for backward compatibility.

    Recommendation: Use /api/barcode/scan instead.
    """
    return jsonify({
        'error': 'OCR scanning deprecated. Please use /api/barcode/scan with a barcode number.',
        'deprecated': True,
        'message': 'Send POST to /api/barcode/scan with {"barcode": "1234567890"}'
    }), 410  # 410 Gone - resource no longer available


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

    product_data = data['product']

    # Get user profile for personalized evaluation
    profile = get_user_profile(DEMO_USER_ID)

    if not profile:
        return jsonify({'error': 'User profile not found'}), 404

    try:
        # Get nutrition agent service
        agent_service = get_nutrition_agent_service()

        # Run comprehensive evaluation
        evaluation = run_async(agent_service.evaluate_product(product_data, profile))

        return jsonify({
            'success': True,
            'evaluation': evaluation
        }), 200

    except Exception as e:
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_nutrition():
    """
    DEPRECATED: Old AI analysis endpoint.
    NEW: Use /api/agent/evaluate for comprehensive agent-based evaluation.

    This endpoint remains for backward compatibility but is deprecated.
    """
    data = request.get_json()

    if not data or 'nutrition_data' not in data:
        return jsonify({'error': 'Missing nutrition data'}), 400

    # Check if we should use the new agent system
    if USE_NUTRITION_AGENT and 'product' in data:
        # Redirect to new agent evaluation
        return evaluate_with_agent()

    nutrition_data = data['nutrition_data']

    # Get demo user profile for personalized analysis
    profile = get_user_profile(DEMO_USER_ID)

    try:
        # Legacy fallback - basic demo analysis
        if USE_AI_MODEL:
            analysis = ai_analyze(nutrition_data, profile)
        else:
            analysis = generate_demo_analysis(nutrition_data, profile)

        return jsonify({
            'success': True,
            'analysis': analysis,
            'nutrition_data': nutrition_data
        }), 200

    except Exception as e:
        return jsonify({'error': f'AI analysis failed: {str(e)}'}), 500


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
            'nutrition': ['POST /api/barcode/scan', 'POST /api/agent/evaluate', 'POST /api/agent/chat'],
            'weight': ['POST /api/weight', 'GET /api/weight/history']
        },
        'demo': 'Open demo.html in your browser to test!'
    }), 200

@app.route('/api/profile/setup', methods=['POST'])
def initial_profile_setup():
    """Initial profile setup - for first-time user onboarding."""
    data = request.get_json() or {}
    print("[DEBUG] Initial profile setup called with:", data)

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
        print("[DEBUG] Height parse error:", e)
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

    print(f"[DEBUG] Saving initial profile: {data}")

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


    

    fetch('http://localhost:5000/api/profile/setup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        height: "5'8",
        weight: 150,
        goal_type: 'weight_loss',
        activity_level: 'moderately_active',
        diet_type: 'standard'
    })
})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("AI Nutrition Help API - HACKATHON DEMO MODE")
    print("="*70)
    print("\n⚠️  NO AUTHENTICATION - For demo purposes only!\n")
    print("API Endpoints (all use demo user):")
    print("  Profile:")
    print("    GET    http://localhost:5000/api/profile")
    print("    PUT    http://localhost:5000/api/profile")
    print("\n  Nutrition & AI:")
    print("    POST   http://localhost:5000/api/barcode/scan")
    print("    POST   http://localhost:5000/api/agent/evaluate")
    print("    POST   http://localhost:5000/api/agent/chat")
    print("\n  Weight Tracking:")
    print("    POST   http://localhost:5000/api/weight")
    print("    GET    http://localhost:5000/api/weight/history")
    print("\n" + "="*70)
    print("\n🚀 Open demo.html in your browser to test!")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
