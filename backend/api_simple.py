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
    update_user_profile,
    get_user_profile,
    log_nutrition,
    get_nutrition_logs,
    add_weight_entry,
    get_weight_history,
    calculate_bmi
)
from backend.nutrition_reader import extract_text_from_image, parse_nutrition_info

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
# SIMPLIFIED ENDPOINTS - NO AUTH REQUIRED
# ============================================================================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get demo user's profile."""
    profile = get_user_profile(DEMO_USER_ID)
    if profile:
        return jsonify({'success': True, 'profile': profile}), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404


@app.route('/api/profile', methods=['PUT', 'POST'])
def update_profile():
    """Update demo user profile."""
    data = request.get_json()

    # Auto-calculate BMI if height and weight provided
    if 'height_cm' in data and 'current_weight_kg' in data:
        data['bmi'] = calculate_bmi(data['current_weight_kg'], data['height_cm'])

    success = update_user_profile(DEMO_USER_ID, data)

    if success:
        profile = get_user_profile(DEMO_USER_ID)
        return jsonify({'success': True, 'message': 'Profile updated', 'profile': profile}), 200
    else:
        return jsonify({'error': 'Failed to update profile'}), 400


@app.route('/api/scan', methods=['POST'])
def scan_nutrition_label():
    """
    Upload and scan a nutrition label image.
    No authentication required for hackathon demo.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"demo_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Extract nutrition data using OCR
            ocr_text = extract_text_from_image(filepath)
            nutrition_data = parse_nutrition_info(ocr_text)

            return jsonify({
                'success': True,
                'nutrition_data': nutrition_data,
                'image_path': filepath,
                'message': 'Nutrition label scanned successfully'
            }), 200

        except Exception as e:
            return jsonify({'error': f'Failed to scan image: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Use jpg, png, gif, or bmp'}), 400


@app.route('/api/analyze', methods=['POST'])
def analyze_nutrition():
    """
    Send nutrition data to AI for analysis.
    Simplified version - uses demo user profile.
    """
    data = request.get_json()

    if not data or 'nutrition_data' not in data:
        return jsonify({'error': 'Missing nutrition data'}), 400

    nutrition_data = data['nutrition_data']

    # Get demo user profile for personalized analysis
    profile = get_user_profile(DEMO_USER_ID)

    try:
        # Prepare structured input for your custom AI model
        ai_input = {
            'nutrition_data': nutrition_data,
            'user_profile': {
                'goal_type': profile.get('goal_type', 'general_health'),
                'diet_type': profile.get('diet_type', 'standard'),
                'daily_calorie_target': profile.get('daily_calorie_target'),
                'daily_protein_target_g': profile.get('daily_protein_target_g'),
                'daily_carbs_target_g': profile.get('daily_carbs_target_g'),
                'daily_fat_target_g': profile.get('daily_fat_target_g'),
                'allergies': profile.get('allergies'),
                'dietary_restrictions': profile.get('dietary_restrictions')
            }
        }

        # TODO: Replace this with your custom trained AI model
        # Example integration patterns:

        # OPTION 1: Local model (TensorFlow/PyTorch)
        # from your_model import NutritionAnalyzer
        # model = NutritionAnalyzer.load('path/to/your/model')
        # analysis = model.predict(ai_input)

        # OPTION 2: API endpoint to your model server
        # import requests
        # response = requests.post('http://your-model-api.com/analyze', json=ai_input)
        # analysis = response.json()['analysis']

        # OPTION 3: Hugging Face model
        # from transformers import pipeline
        # analyzer = pipeline('text-generation', model='your-model-name')
        # analysis = analyzer(str(ai_input), max_length=500)[0]['generated_text']

        # Use custom AI model if available, otherwise use demo
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


@app.route('/api/log', methods=['POST'])
def create_nutrition_log():
    """Log nutrition data for demo user."""
    data = request.get_json()

    if not data or 'nutrition_data' not in data:
        return jsonify({'error': 'Missing nutrition data'}), 400

    nutrition_json = json.dumps(data['nutrition_data'])

    log_id = log_nutrition(
        user_id=DEMO_USER_ID,
        nutrition_json=nutrition_json,
        meal_type=data.get('meal_type', 'other'),
        food_name=data.get('food_name', 'Unknown Food'),
        notes=data.get('notes'),
        image_path=data.get('image_path')
    )

    if log_id:
        return jsonify({
            'success': True,
            'log_id': log_id,
            'message': 'Nutrition logged successfully'
        }), 201
    else:
        return jsonify({'error': 'Failed to log nutrition'}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get nutrition logs for demo user."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    logs = get_nutrition_logs(DEMO_USER_ID, start_date, end_date)

    # Calculate totals
    total_calories = sum(log.get('calories', 0) or 0 for log in logs)
    total_protein = sum(log.get('protein_g', 0) or 0 for log in logs)
    total_carbs = sum(log.get('total_carbs_g', 0) or 0 for log in logs)
    total_fat = sum(log.get('total_fat_g', 0) or 0 for log in logs)

    return jsonify({
        'success': True,
        'logs': logs,
        'totals': {
            'calories': total_calories,
            'protein_g': round(total_protein, 1),
            'carbs_g': round(total_carbs, 1),
            'fat_g': round(total_fat, 1)
        },
        'count': len(logs)
    }), 200


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
            'nutrition': ['POST /api/scan', 'POST /api/analyze', 'POST /api/log', 'GET /api/logs'],
            'weight': ['POST /api/weight', 'GET /api/weight/history']
        },
        'demo': 'Open demo.html in your browser to test!'
    }), 200


if __name__ == '__main__':
    print("\n" + "="*70)
    print("AI Nutrition Help API - HACKATHON DEMO MODE")
    print("="*70)
    print("\n⚠️  NO AUTHENTICATION - For demo purposes only!\n")
    print("API Endpoints (all use demo user):")
    print("  Profile:")
    print("    GET    http://localhost:5000/api/profile")
    print("    PUT    http://localhost:5000/api/profile")
    print("\n  Nutrition:")
    print("    POST   http://localhost:5000/api/scan")
    print("    POST   http://localhost:5000/api/analyze")
    print("    POST   http://localhost:5000/api/log")
    print("    GET    http://localhost:5000/api/logs")
    print("\n  Weight Tracking:")
    print("    POST   http://localhost:5000/api/weight")
    print("    GET    http://localhost:5000/api/weight/history")
    print("\n" + "="*70)
    print("\n🚀 Open demo.html in your browser to test!")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
