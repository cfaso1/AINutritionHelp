# 🍎 AI Nutrition Help

Scan product barcodes, get AI-powered nutrition analysis, and reach your health goals with personalized recommendations from multi-agent AI system.

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
- 🔍 **Barcode Scanner** - Scan product barcodes or upload barcode images to retrieve nutrition data
- 🤖 **Multi-Agent AI System** - 3 specialized agents (Health, Fitness, Price)
- ❤️ **Health Evaluator** - Analyzes nutrition alignment with your health goals
- 💪 **Fitness Evaluator** - Evaluates products for your fitness objectives
- 💰 **Price Evaluator** - Assesses value for money and suggests alternatives
- 🎯 **Health Goals** - Set weight, height, fitness habits, and dietary preferences
- 🔐 **User Authentication** - Login, register, or use demo account

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
├── run.py                              # Start the server
├── requirements.txt                    # Python dependencies
│
├── backend/                            # Backend API
│   ├── api_simple.py                  # REST API with auth endpoints
│   ├── database.py                    # SQLite database with price tracking
│   ├── nutrition_agent_service.py     # Integration layer for nutrition agent
│   ├── uploads/                       # Uploaded images (auto-created)
│   └── nutrition_app.db               # SQLite database (auto-created)
│
├── frontend/                           # Frontend UI
│   ├── demo.html                      # Single-page app with all features
│   └── barcode_scanner.js             # Barcode scanning and AI analysis
│
└── nutrition_agent/                    # AI Agent System
    ├── agents/                        # Agent implementations
    │   ├── barcode_scanner.py         # Barcode scanning agent
    │   ├── health_evaluator.py        # Health analysis agent
    │   ├── fitness_evaluator.py       # Fitness evaluation agent
    │   └── price_evaluator.py         # Price analysis agent
    ├── models/                        # Data models
    │   ├── product.py                 # Product model
    │   └── user_profile.py            # User profile model
    └── services/                      # External services
        ├── llm_service.py             # Anthropic/Claude AI service
        └── barcode_api.py             # Barcode lookup API service
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

### 3. Scan Product Barcodes (🔍 Scanner Tab)
- **Option 1**: Enter barcode number manually and click "Scan Barcode"
- **Option 2**: Upload barcode image and extract barcode automatically
- Review product information and nutrition facts

### 4. Get AI Analysis
- Click "🤖 Get AI Analysis"
- View comprehensive evaluation from 3 AI agents:
  - **Health Agent**: Nutrition alignment score and recommendations
  - **Fitness Agent**: Fitness goal compatibility and timing suggestions
  - **Price Agent**: Value assessment and alternatives

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:5000/api`

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Profile & Goals
- `GET /profile` - Get user profile and health goals
- `PUT /profile` - Update profile and goals

### Barcode Scanning & AI Evaluation
- `POST /barcode/scan` - Scan barcode number and retrieve product data
- `POST /barcode/image` - Upload barcode image and extract barcode automatically
- `POST /agent/evaluate` - Get comprehensive AI evaluation (3 agents)

### Weight Tracking
- `POST /weight` - Log weight entry
- `GET /weight/history` - Get weight history

### Health Check
- `GET /health` - API status

### Deprecated
- `POST /scan` - ❌ Old OCR scanner (use `/barcode/scan` instead)
- `POST /analyze` - ❌ Old analysis (use `/agent/evaluate` instead)

---

## 🤖 Multi-Agent AI System

The application uses a **three-agent architecture** powered by Anthropic's Claude API for intelligent food analysis:

### Agent Architecture

**1. Health Evaluator Agent**
- Analyzes nutritional content against user's health goals
- Scores products 0-100 based on macro/micronutrient profile
- Provides specific pros and cons
- Considers dietary restrictions and allergies

**2. Fitness Evaluator Agent**
- Evaluates alignment with fitness objectives
- Recommends optimal consumption timing (pre/post workout)
- Scores based on protein, carbs, and activity level
- Customized for muscle gain, weight loss, or maintenance

**3. Price Evaluator Agent**
- Assesses value for money
- Compares unit price across similar products
- Suggests budget-friendly alternatives
- Tracks spending patterns

### Parallel Execution
All three agents run **simultaneously** using `asyncio.gather()` for optimal performance, providing comprehensive analysis in seconds.

### Data Flow
```
Barcode → Product Lookup → User Profile + Product Data
                          ↓
          [Health Agent | Fitness Agent | Price Agent]
                          ↓
              Combined Evaluation Results
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

### Barcode Scanner or AI Agents Not Working
- Verify API keys are set in `.env` file
- Check `ANTHROPIC_API_KEY` for AI agents
- Check `BARCODE_LOOKUP_API_KEY` for barcode scanning
- Restart server after adding API keys

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

### Environment Variables
Create `.env` file in project root:

```env
# Required for AI Agent System
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx      # For AI evaluations
BARCODE_LOOKUP_API_KEY=xxxxxxxxxxxxx        # For barcode scanning

# Optional
FLASK_DEBUG=True
DATABASE_PATH=backend/nutrition_app.db
UPLOAD_FOLDER=backend/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

**Get API Keys:**
- **Anthropic (Claude)**: https://console.anthropic.com/
- **Barcode Lookup**: https://www.barcodelookup.com/api

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

**AI & External Services:**
- Anthropic Claude API (for multi-agent AI analysis)
- Barcode Lookup API (for product information retrieval)

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
✅ **Barcode Scanner** - Instant product lookup via barcode API
✅ **Multi-Agent AI System** - 3 specialized evaluators (Health, Fitness, Price)
✅ **Barcode Image Scanner** - Upload images to automatically detect barcodes
✅ **AI-Powered Recommendations** - Personalized based on user goals
✅ **Responsive UI** - Modern design with tab navigation
✅ **Database Migration** - Backward compatible with existing data

---

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Mobile app development (API is ready)
- Recipe recommendations engine
- Social features (meal sharing, challenges)
- Multi-language support
- Export functionality (PDF/CSV reports)
- Integration with fitness trackers
- Real-time barcode scanning via camera

---

## 📞 Support

**Issues?**
- Check API is running: `http://localhost:5000/api/health`
- Review browser console for JavaScript errors
- Verify API keys are configured in `.env`
- Check database file exists: `backend/nutrition_app.db`
- Ensure Python 3.8+ is installed

**Questions?**
- Review API documentation in this README
- Check code comments in `backend/api_simple.py`
- See agent integration in `backend/nutrition_agent_service.py`
- Explore agent code in `nutrition_agent/` directory

---

**Made with ❤️ for better nutrition tracking**
