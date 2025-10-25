#!/usr/bin/env python3
"""
REST API for AI Nutrition Help Application
Provides endpoints for user authentication, nutrition scanning, and AI analysis.

INSTALLATION:
    pip install flask flask-cors anthropic pillow pytesseract

USAGE:
    python api.py

API ENDPOINTS:
    POST   /api/auth/register          - Create new user account
    POST   /api/auth/login             - User login
    GET    /api/user/profile           - Get user profile
    PUT    /api/user/profile           - Update user profile

    POST   /api/nutrition/scan         - Upload and scan nutrition label
    POST   /api/nutrition/analyze      - Send nutrition data to AI for analysis
    GET    /api/nutrition/logs         - Get nutrition logs
    POST   /api/nutrition/log          - Manually log nutrition

    POST   /api/weight                 - Add weight entry
    GET    /api/weight/history         - Get weight history
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path

# Import your existing modules
from database import (
    init_database,
    create_user,
    authenticate_user,
    update_user_profile,
    get_user_profile,
    log_nutrition,
    get_nutrition_logs,
    add_weight_entry,
    get_weight_history,
    calculate_bmi
)
from nutrition_reader import extract_text_from_image, parse_nutrition_info

# Optional: Import AI library (uncomment when you add your API key)
# import anthropic

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # For session management

# Configure CORS to allow frontend requests
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"])

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database on startup
init_database()


def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)

    return decorated_function


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register a new user account.

    Request JSON:
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }

    Response:
        {
            "success": true,
            "user_id": 1,
            "message": "User created successfully"
        }
    """
    data = request.get_json()

    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    user_id = create_user(data['username'], data['email'], data['password'])

    if user_id:
        session['user_id'] = user_id
        session['username'] = data['username']
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': data['username'],
            'message': 'User created successfully'
        }), 201
    else:
        return jsonify({'error': 'Username or email already exists'}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and create session.

    Request JSON:
        {
            "username": "string",
            "password": "string"
        }

    Response:
        {
            "success": true,
            "user_id": 1,
            "username": "string",
            "email": "string"
        }
    """
    data = request.get_json()

    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400

    auth_result = authenticate_user(data['username'], data['password'])

    if auth_result:
        session['user_id'] = auth_result['user_id']
        session['username'] = auth_result['username']
        return jsonify({
            'success': True,
            **auth_result
        }), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated."""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user_id': session['user_id'],
            'username': session.get('username')
        }), 200
    else:
        return jsonify({'authenticated': False}), 200


# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================

@app.route('/api/user/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    Get current user's profile.

    Response:
        {
            "username": "string",
            "email": "string",
            "date_of_birth": "YYYY-MM-DD",
            "gender": "string",
            "height_cm": 175.0,
            "current_weight_kg": 75.0,
            ...
        }
    """
    user_id = session['user_id']
    profile = get_user_profile(user_id)

    if profile:
        return jsonify(profile), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404


@app.route('/api/user/profile', methods=['PUT'])
@require_auth
def update_profile():
    """
    Update user profile.

    Request JSON (all fields optional):
        {
            "date_of_birth": "YYYY-MM-DD",
            "gender": "male|female|other|prefer_not_to_say",
            "height_cm": 175.0,
            "current_weight_kg": 75.0,
            "goal_type": "weight_loss|weight_gain|muscle_gain|...",
            "target_weight_kg": 70.0,
            "activity_level": "sedentary|lightly_active|...",
            "diet_type": "standard|vegetarian|vegan|...",
            "allergies": "string",
            "dietary_restrictions": "string",
            "daily_calorie_target": 2000,
            "daily_protein_target_g": 150,
            "daily_carbs_target_g": 200,
            "daily_fat_target_g": 65
        }
    """
    user_id = session['user_id']
    data = request.get_json()

    # Auto-calculate BMI if height and weight provided
    if 'height_cm' in data and 'current_weight_kg' in data:
        data['bmi'] = calculate_bmi(data['current_weight_kg'], data['height_cm'])

    success = update_user_profile(user_id, data)

    if success:
        return jsonify({'success': True, 'message': 'Profile updated'}), 200
    else:
        return jsonify({'error': 'Failed to update profile'}), 400


# ============================================================================
# NUTRITION SCANNING & AI ENDPOINTS
# ============================================================================

@app.route('/api/nutrition/scan', methods=['POST'])
@require_auth
def scan_nutrition_label():
    """
    Upload and scan a nutrition label image.

    Request:
        multipart/form-data with 'image' file

    Response:
        {
            "success": true,
            "nutrition_data": { ... parsed nutrition JSON ... },
            "image_path": "uploads/filename.jpg"
        }
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        # Save file securely
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{session['user_id']}_{timestamp}_{filename}"
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
        return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/nutrition/analyze', methods=['POST'])
@require_auth
def analyze_nutrition():
    """
    Send nutrition data to AI for analysis.

    Request JSON:
        {
            "nutrition_data": { ... nutrition JSON ... },
            "user_context": {  // optional
                "goal_type": "muscle_gain",
                "dietary_restrictions": "vegan",
                "allergies": "peanuts"
            }
        }

    Response:
        {
            "success": true,
            "analysis": "AI-generated analysis text",
            "recommendations": "AI recommendations"
        }
    """
    data = request.get_json()

    if not data or 'nutrition_data' not in data:
        return jsonify({'error': 'Missing nutrition data'}), 400

    nutrition_data = data['nutrition_data']
    user_context = data.get('user_context', {})

    # Get user profile for personalized analysis
    user_id = session['user_id']
    profile = get_user_profile(user_id)

    try:
        # Build AI prompt
        prompt = f"""Analyze this nutrition label data and provide a comprehensive health assessment.

Nutrition Data:
{json.dumps(nutrition_data, indent=2)}

User Profile:
- Goal: {profile.get('goal_type', 'general health')}
- Diet Type: {profile.get('diet_type', 'standard')}
- Allergies: {profile.get('allergies', 'none')}
- Dietary Restrictions: {profile.get('dietary_restrictions', 'none')}
- Daily Calorie Target: {profile.get('daily_calorie_target', 'not set')} kcal
- Daily Protein Target: {profile.get('daily_protein_target_g', 'not set')} g

Please provide:
1. Overall Health Assessment: Is this food healthy? Rate it 1-10.
2. Key Nutritional Highlights: What stands out (high/low nutrients)?
3. Dietary Compatibility: Does this fit the user's diet type and goals?
4. Warnings/Concerns: Any red flags (high sodium, trans fats, added sugars)?
5. Recommendations: Who should/shouldn't eat this? How it fits user's goals.
6. Portion Guidance: Should they eat the whole thing or portion it?

Be specific, actionable, and personalized to the user's goals."""

        # TODO: Uncomment and add your AI API key
        # For now, return a placeholder response

        # OPTION 1: Using Anthropic Claude (recommended)
        # client = anthropic.Anthropic(api_key="YOUR_API_KEY_HERE")
        # message = client.messages.create(
        #     model="claude-3-5-sonnet-20241022",
        #     max_tokens=1024,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # analysis = message.content[0].text

        # OPTION 2: Using OpenAI GPT
        # import openai
        # openai.api_key = "YOUR_API_KEY_HERE"
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # analysis = response.choices[0].message.content

        # PLACEHOLDER RESPONSE (remove when you add AI)
        analysis = f"""AI Analysis Placeholder:

1. Overall Health Assessment: [AI will analyze here]
2. Nutritional Highlights: [AI will identify key nutrients]
3. Dietary Compatibility: [AI will check against {profile.get('goal_type', 'goals')}]
4. Warnings: [AI will flag concerns]
5. Recommendations: [AI will provide personalized advice]

To enable AI analysis, add your API key in api.py around line 390.
The nutrition data has been successfully scanned and is ready for AI analysis!"""

        return jsonify({
            'success': True,
            'analysis': analysis,
            'prompt_used': prompt  # For debugging
        }), 200

    except Exception as e:
        return jsonify({'error': f'AI analysis failed: {str(e)}'}), 500


@app.route('/api/nutrition/log', methods=['POST'])
@require_auth
def create_nutrition_log():
    """
    Manually log nutrition data.

    Request JSON:
        {
            "nutrition_data": { ... },
            "meal_type": "breakfast|lunch|dinner|snack|other",
            "food_name": "string",
            "notes": "string"  // optional
        }
    """
    user_id = session['user_id']
    data = request.get_json()

    if not data or 'nutrition_data' not in data:
        return jsonify({'error': 'Missing nutrition data'}), 400

    nutrition_json = json.dumps(data['nutrition_data'])

    log_id = log_nutrition(
        user_id=user_id,
        nutrition_json=nutrition_json,
        meal_type=data.get('meal_type', 'other'),
        food_name=data.get('food_name'),
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


@app.route('/api/nutrition/logs', methods=['GET'])
@require_auth
def get_logs():
    """
    Get nutrition logs for current user.

    Query params:
        start_date: YYYY-MM-DD (optional)
        end_date: YYYY-MM-DD (optional)

    Response:
        {
            "success": true,
            "logs": [ ... array of nutrition log objects ... ],
            "total_calories": 1500,
            "total_protein_g": 75
        }
    """
    user_id = session['user_id']
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    logs = get_nutrition_logs(user_id, start_date, end_date)

    # Calculate totals
    total_calories = sum(log.get('calories', 0) or 0 for log in logs)
    total_protein = sum(log.get('protein_g', 0) or 0 for log in logs)

    return jsonify({
        'success': True,
        'logs': logs,
        'total_calories': total_calories,
        'total_protein_g': round(total_protein, 1)
    }), 200


# ============================================================================
# WEIGHT TRACKING ENDPOINTS
# ============================================================================

@app.route('/api/weight', methods=['POST'])
@require_auth
def add_weight():
    """
    Add a weight tracking entry.

    Request JSON:
        {
            "weight_kg": 75.5,
            "notes": "Morning weigh-in"  // optional
        }
    """
    user_id = session['user_id']
    data = request.get_json()

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
@require_auth
def get_weight():
    """
    Get weight history for current user.

    Query params:
        limit: number of entries (default 30)

    Response:
        {
            "success": true,
            "history": [ ... ],
            "current_weight_kg": 75.5,
            "trend": "increasing|decreasing|stable"
        }
    """
    user_id = session['user_id']
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
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Nutrition Help API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint."""
    return jsonify({
        'message': 'AI Nutrition Help API',
        'version': '1.0.0',
        'documentation': 'See api.py for endpoint documentation',
        'endpoints': {
            'auth': ['/api/auth/register', '/api/auth/login', '/api/auth/logout'],
            'user': ['/api/user/profile'],
            'nutrition': ['/api/nutrition/scan', '/api/nutrition/analyze', '/api/nutrition/log', '/api/nutrition/logs'],
            'weight': ['/api/weight', '/api/weight/history']
        }
    }), 200


if __name__ == '__main__':
    print("\n" + "="*70)
    print("AI Nutrition Help API Server")
    print("="*70)
    print("\nAPI Documentation:")
    print("  Authentication:")
    print("    POST   http://localhost:5000/api/auth/register")
    print("    POST   http://localhost:5000/api/auth/login")
    print("    POST   http://localhost:5000/api/auth/logout")
    print("\n  User Profile:")
    print("    GET    http://localhost:5000/api/user/profile")
    print("    PUT    http://localhost:5000/api/user/profile")
    print("\n  Nutrition:")
    print("    POST   http://localhost:5000/api/nutrition/scan")
    print("    POST   http://localhost:5000/api/nutrition/analyze")
    print("    POST   http://localhost:5000/api/nutrition/log")
    print("    GET    http://localhost:5000/api/nutrition/logs")
    print("\n  Weight Tracking:")
    print("    POST   http://localhost:5000/api/weight")
    print("    GET    http://localhost:5000/api/weight/history")
    print("\n" + "="*70)
    print("\nStarting server on http://localhost:5000")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
