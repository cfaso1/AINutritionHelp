# AI Nutrition Help - API Documentation

## Overview

This REST API connects your nutrition database and OCR scanner to your frontend website, with AI-powered nutrition analysis.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables (Optional)

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run the API Server

```bash
python api.py
```

The server will start on `http://localhost:5000`

### 4. Test the API

Open `frontend_example.html` in your browser to test all endpoints with a visual interface.

---

## API Endpoints

### Authentication

#### Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}

Response:
{
  "success": true,
  "user_id": 1,
  "username": "john_doe",
  "message": "User created successfully"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123"
}

Response:
{
  "success": true,
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

#### Logout
```http
POST /api/auth/logout

Response:
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### Check Authentication Status
```http
GET /api/auth/check

Response:
{
  "authenticated": true,
  "user_id": 1,
  "username": "john_doe"
}
```

---

### User Profile

#### Get User Profile
```http
GET /api/user/profile
Authentication: Required

Response:
{
  "username": "john_doe",
  "email": "john@example.com",
  "date_of_birth": "1990-05-15",
  "gender": "male",
  "height_cm": 175.0,
  "current_weight_kg": 75.0,
  "goal_type": "muscle_gain",
  "target_weight_kg": 80.0,
  "activity_level": "moderately_active",
  "bmi": 24.5,
  "daily_calorie_target": 2500,
  ...
}
```

#### Update User Profile
```http
PUT /api/user/profile
Content-Type: application/json
Authentication: Required

{
  "height_cm": 175,
  "current_weight_kg": 75,
  "goal_type": "muscle_gain",
  "diet_type": "high_protein",
  "daily_calorie_target": 2500
}

Response:
{
  "success": true,
  "message": "Profile updated"
}
```

---

### Nutrition Scanning & AI

#### Scan Nutrition Label
```http
POST /api/nutrition/scan
Content-Type: multipart/form-data
Authentication: Required

FormData:
- image: [File]

Response:
{
  "success": true,
  "nutrition_data": {
    "serving_information": {
      "serving_size": "1 bar (50g)",
      "servings_per_container": "2"
    },
    "calories": {
      "total": "210",
      "from_fat": "70"
    },
    "macronutrients": {
      "protein": {"amount_g": "12"},
      "fat": {"total_g": "8", ...},
      "carbohydrates": {"total_g": "25", ...}
    },
    "micronutrients": {...}
  },
  "image_path": "uploads/1_20250125_143022_label.jpg",
  "message": "Nutrition label scanned successfully"
}
```

#### AI Analysis
```http
POST /api/nutrition/analyze
Content-Type: application/json
Authentication: Required

{
  "nutrition_data": {
    // ... nutrition data from scan endpoint
  }
}

Response:
{
  "success": true,
  "analysis": "AI-generated comprehensive nutrition analysis..."
}
```

#### Log Nutrition Manually
```http
POST /api/nutrition/log
Content-Type: application/json
Authentication: Required

{
  "nutrition_data": {...},
  "meal_type": "breakfast",
  "food_name": "Protein Bar",
  "notes": "Post-workout snack"
}

Response:
{
  "success": true,
  "log_id": 5,
  "message": "Nutrition logged successfully"
}
```

#### Get Nutrition Logs
```http
GET /api/nutrition/logs?start_date=2025-01-25&end_date=2025-01-25
Authentication: Required

Response:
{
  "success": true,
  "logs": [
    {
      "log_id": 1,
      "food_name": "Protein Bar",
      "calories": 210,
      "protein_g": 12,
      "meal_type": "snack",
      "log_date": "2025-01-25",
      ...
    }
  ],
  "total_calories": 1850,
  "total_protein_g": 95.5
}
```

---

### Weight Tracking

#### Add Weight Entry
```http
POST /api/weight
Content-Type: application/json
Authentication: Required

{
  "weight_kg": 75.5,
  "notes": "Morning weigh-in"
}

Response:
{
  "success": true,
  "weight_id": 3,
  "message": "Weight logged successfully"
}
```

#### Get Weight History
```http
GET /api/weight/history?limit=30
Authentication: Required

Response:
{
  "success": true,
  "history": [
    {
      "weight_id": 3,
      "weight_kg": 75.5,
      "recorded_at": "2025-01-25 08:30:00",
      "notes": "Morning weigh-in"
    }
  ],
  "current_weight_kg": 75.5,
  "trend": "decreasing"
}
```

---

## Frontend Integration Examples

### JavaScript (Vanilla)

```javascript
// Configuration
const API_URL = 'http://localhost:5000/api';

// Login
async function login(username, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // Important for sessions
    body: JSON.stringify({ username, password })
  });
  return await response.json();
}

// Scan nutrition label
async function scanLabel(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);

  const response = await fetch(`${API_URL}/nutrition/scan`, {
    method: 'POST',
    credentials: 'include',
    body: formData
  });
  return await response.json();
}

// AI Analysis
async function analyzeNutrition(nutritionData) {
  const response = await fetch(`${API_URL}/nutrition/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ nutrition_data: nutritionData })
  });
  return await response.json();
}
```

### React Example

```jsx
import { useState } from 'react';

function NutritionScanner() {
  const [nutritionData, setNutritionData] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('http://localhost:5000/api/nutrition/scan', {
      method: 'POST',
      credentials: 'include',
      body: formData
    });

    const result = await response.json();
    if (result.success) {
      setNutritionData(result.nutrition_data);
    }
  };

  const analyzeFood = async () => {
    const response = await fetch('http://localhost:5000/api/nutrition/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ nutrition_data: nutritionData })
    });

    const result = await response.json();
    if (result.success) {
      setAnalysis(result.analysis);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleImageUpload} accept="image/*" />
      {nutritionData && (
        <div>
          <h3>Scanned Data:</h3>
          <pre>{JSON.stringify(nutritionData, null, 2)}</pre>
          <button onClick={analyzeFood}>Analyze with AI</button>
        </div>
      )}
      {analysis && <div><h3>AI Analysis:</h3><p>{analysis}</p></div>}
    </div>
  );
}
```

---

## Adding AI Analysis

To enable AI-powered nutrition analysis, you need an API key from either:

### Option 1: Anthropic Claude (Recommended)

1. Sign up at https://console.anthropic.com/
2. Get your API key
3. Update [api.py](api.py:390) around line 390:

```python
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# In the analyze_nutrition function:
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)
analysis = message.content[0].text
```

### Option 2: OpenAI GPT

1. Sign up at https://platform.openai.com/
2. Get your API key
3. Update the analyze function to use OpenAI:

```python
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
analysis = response.choices[0].message.content
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

To add more origins, edit [api.py](api.py:43) line 43:

```python
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://your-frontend-domain.com"
])
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing/invalid data)
- `401` - Unauthorized (login required)
- `404` - Not Found
- `500` - Internal Server Error

---

## Testing

### Using curl

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"pass123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"test","password":"pass123"}'

# Get profile (requires cookie from login)
curl -X GET http://localhost:5000/api/user/profile \
  -b cookies.txt
```

### Using the HTML Test Interface

Simply open `frontend_example.html` in your browser and test all endpoints visually!

---

## Production Deployment

For production deployment:

1. Use a production WSGI server (not Flask's built-in server):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

2. Set up proper environment variables
3. Use HTTPS
4. Configure proper CORS origins
5. Set `app.config['SESSION_COOKIE_SECURE'] = True`
6. Use a production database (PostgreSQL recommended)

---

## Support

For issues or questions:
- Check the code comments in [api.py](api.py)
- Review [database.py](database.py) for database functions
- Review [nutrition_reader.py](nutrition_reader.py) for OCR functions
- Test with [frontend_example.html](frontend_example.html)

Good luck with your hackathon!
