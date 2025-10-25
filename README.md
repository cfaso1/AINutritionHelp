# 🍎 AI Nutrition Help

Scan nutrition labels, track your eating habits, and reach your health goals with AI-powered recommendations.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python run.py

# 3. Open the app
# Open: frontend/demo.html in your browser
```

**That's it!** Use the demo account or create your own.

---

## ✨ Features

### Core Features
- 📸 **OCR Nutrition Scanner** - Upload images and extract nutrition data automatically
- ✅ **Data Validation** - Confirms extracted data and prompts for missing values
- 💰 **Price Tracking** - Track food costs alongside nutrition data
- 🎯 **Health Goals** - Set weight, height, fitness habits, and dietary preferences
- 🔐 **User Authentication** - Login, register, or use demo account
- 📊 **Food Log** - Track eating history with daily totals
- 🤖 **AI Analysis** - Get personalized recommendations (demo mode, ready for real AI)

### Extracted Nutrition Data (10+ Fields)
- Calories, Protein, Fat (total, saturated, trans)
- Carbohydrates (total, fiber), Sugar (total, added)
- Sodium, Cholesterol, Potassium
- Vitamins (A, C, D), Calcium, Iron
- Serving size, Servings per container

---

## 📁 Project Structure

```
AINutritionHelp/
├── run.py                      # Start the server
├── requirements.txt            # Python dependencies
│
├── backend/                    # Backend API
│   ├── api_simple.py          # REST API with auth endpoints
│   ├── database.py            # SQLite database with price tracking
│   ├── nutrition_reader.py   # OCR nutrition label scanner
│   ├── ai_model.py            # AI model integration (demo mode)
│   ├── uploads/               # Uploaded images (auto-created)
│   └── nutrition_app.db       # SQLite database (auto-created)
│
└── frontend/                   # Frontend UI
    └── demo.html              # Single-page app with all features
```

---

## 🎯 How to Use

### 1. Login
- **Demo Account:** Click "Use Demo Account" for instant access
- **Register:** Create your own account with username/email/password
- **Login:** Use your credentials

### 2. Set Health Goals (🎯 Health Goals Tab)
Fill in your information:
- **Goal:** Weight loss, muscle gain, general health, etc.
- **Personal Info:** Weight (kg), Height (cm), Date of birth
- **Fitness Habits:** Sedentary → Extremely active (5 levels)
- **Diet Preferences:** Vegetarian, vegan, keto, standard, etc.
- **Allergies:** Comma-separated list

Click "Save Health Goals" - BMI is calculated automatically.

### 3. Scan Nutrition Labels (📸 Scanner Tab)
- Upload image (click or drag-and-drop)
- Click "Scan Label"
- Review extracted data
- Fill in any missing fields manually
- Enter **food name** and **price** (optional)
- Select meal type (breakfast, lunch, dinner, snack)

### 4. Get AI Analysis
- Click "🤖 Analyze with AI"
- View personalized recommendations based on your goals

### 5. Save to Food Log
- Click "💾 Save to Log"
- Food item saved with nutrition data, price, and timestamp

### 6. View Food History (📊 Food Log Tab)
- See daily totals: Calories, Protein, Carbs, Fat
- View all logged items with prices
- Click "🔄 Refresh Logs"

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:5000/api`

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Profile & Goals
- `GET /profile` - Get user profile and health goals
- `PUT /profile` - Update profile and goals

### Nutrition Scanning
- `POST /scan` - Upload & scan nutrition label image
- `POST /analyze` - Get AI analysis of nutrition data

### Food Logging
- `POST /log` - Save nutrition data (with price and food name)
- `GET /logs` - Get food logs (defaults to today)

### Weight Tracking
- `POST /weight` - Log weight entry
- `GET /weight/history` - Get weight history

### Health Check
- `GET /health` - API status

---

## 🤖 AI Model Integration

The app is ready for custom AI model integration. Replace the demo analysis in `backend/ai_model.py`.

### Available Data for AI:
```json
{
  "nutrition_data": {
    "calories": {...},
    "macronutrients": {...},
    "micronutrients": {...},
    "serving_information": {...}
  },
  "user_profile": {
    "goal_type": "muscle_gain",
    "activity_level": "very_active",
    "diet_type": "high_protein",
    "current_weight_kg": 80,
    "height_cm": 180,
    "bmi": 24.7,
    "allergies": "...",
    ...
  },
  "food_history": [...]
}
```

### Integration Examples:

**TensorFlow/PyTorch:**
```python
from backend.ai_model import NutritionAnalyzer
model = NutritionAnalyzer.load('path/to/model')
analysis = model.predict(nutrition_data, user_profile)
```

**External API:**
```python
import requests
response = requests.post('https://your-ai-api.com/analyze',
                        json={'nutrition_data': data, 'user_profile': profile})
```

**Hugging Face:**
```python
from transformers import pipeline
analyzer = pipeline('text-generation', model='your-model')
analysis = analyzer(json.dumps(nutrition_data))
```

---

## 💾 Database Schema

### Tables

**users**
- user_id, username, email
- password_hash, password_salt
- created_at, last_login

**user_profiles**
- Personal: date_of_birth, gender, height_cm, current_weight_kg
- Goals: goal_type, target_weight_kg, activity_level
- Diet: diet_type, allergies, dietary_restrictions
- Targets: daily_calorie_target, protein_target_g, carbs_target_g, fat_target_g
- Calculated: bmi

**nutrition_logs**
- Log info: log_date, meal_type, food_name, **price**
- Full data: nutrition_json (complete OCR output)
- Quick access: calories, protein_g, total_fat_g, total_carbs_g
- Metadata: image_path, notes, created_at

**weight_history**
- weight_id, user_id, weight_kg
- recorded_at, notes

---

## 🧪 Testing

### Test API Health
```bash
curl http://localhost:5000/api/health
```

### Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"demo123"}'
```

### Test Profile Update
```bash
curl -X POST http://localhost:5000/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "goal_type": "muscle_gain",
    "current_weight_kg": 80,
    "height_cm": 180,
    "activity_level": "very_active"
  }'
```

---

## 🔧 Troubleshooting

### Server won't start
```bash
# Check Python version (need 3.8+)
python3 --version

# Install dependencies
pip install -r requirements.txt

# Try running directly
python3 backend/api_simple.py
```

### "Tesseract not found"
Install Tesseract OCR:
- **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
- **macOS:** `brew install tesseract`
- **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Frontend can't connect to API
- Verify server is running: `curl http://localhost:5000/api/health`
- Check browser console for errors
- Ensure CORS is enabled (already configured)

### Database errors
```bash
# Reset database (WARNING: deletes all data)
rm backend/nutrition_app.db

# Restart server (will recreate database)
python run.py
```

---

## 📝 Configuration

### Environment Variables (Optional)
Create `.env` file in project root:
```env
FLASK_DEBUG=True
DATABASE_PATH=backend/nutrition_app.db
UPLOAD_FOLDER=backend/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Database Migration
The app automatically migrates existing databases:
- Adds new columns (e.g., `price` field)
- Preserves existing data
- Runs on server startup

---

## 🚀 Production Deployment

For production use, implement:

### Security
- [ ] JWT authentication (password hashing already done)
- [ ] HTTPS/SSL certificates
- [ ] Rate limiting on API endpoints
- [ ] Input sanitization (parameterized queries already used)
- [ ] CORS restrictions (currently allows all origins)

### Database
- [ ] Switch to PostgreSQL or MySQL
- [ ] Database backups
- [ ] Connection pooling

### Infrastructure
- [ ] Deploy to cloud (Heroku, AWS, GCP, Azure)
- [ ] Load balancing
- [ ] CDN for static files
- [ ] Monitoring and logging

### Features
- [ ] Email verification
- [ ] Password reset
- [ ] OAuth/SSO integration
- [ ] Mobile app (API is ready)
- [ ] Barcode scanning
- [ ] Recipe suggestions
- [ ] Export reports (PDF/CSV)

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Flask 3.0.0 (REST API)
- SQLite3 (database)
- Tesseract OCR (image processing)
- Pillow (image handling)

**Frontend:**
- Vanilla HTML5/CSS3/JavaScript
- No frameworks (lightweight)
- Fetch API for HTTP requests

**Optional:**
- Anthropic Claude API (for AI analysis)
- TensorFlow/PyTorch (for custom AI models)

---

## 📊 Demo Account

**Username:** `demo_user`
**Password:** `demo123`
**User ID:** 1

All demo data is isolated to this account. Create your own account for personal use.

---

## 🎯 What's Included

✅ **User Authentication** - Demo implementation with password hashing
✅ **Health Goal Setting** - Comprehensive profile with BMI calculation
✅ **Image OCR Scanner** - Extracts 10+ nutrition fields automatically
✅ **Data Validation** - Checks for missing fields, allows manual input
✅ **Price Tracking** - Track food costs for budget analysis
✅ **Food Logging** - Complete eating history with timestamps
✅ **AI Integration Ready** - Structured data pipeline for custom models
✅ **Responsive UI** - Modern design with tab navigation
✅ **Database Migration** - Backward compatible with existing data

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Real AI model integration
- Mobile app development
- Barcode scanning feature
- Recipe recommendations
- Social features (meal sharing)
- Multi-language support

---

## 📞 Support

**Issues?**
- Check API is running: `http://localhost:5000/api/health`
- Review browser console for JavaScript errors
- Verify Tesseract OCR is installed
- Check database file exists: `backend/nutrition_app.db`

**Questions?**
- Review API documentation above
- Check code comments in `backend/api_simple.py`
- See database schema in `backend/database.py`

---

**Made with ❤️ for better nutrition tracking**
