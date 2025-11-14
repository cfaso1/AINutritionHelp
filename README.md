# 🍎 BalanceBot - AI Nutrition Assistant

An AI-powered nutrition analysis web application that scans product labels, provides personalized health insights, and offers interactive nutrition guidance through an intelligent chatbot.

> **⚠️ Educational Project Disclaimer**
> This is a computer science educational project for demonstration purposes only. Not intended for medical, nutritional, or dietary use. AI-generated information may contain errors—always verify facts independently. Consult qualified healthcare professionals for actual health decisions. The database is periodically reset, and user data may be deleted without notice.

---

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone <your-repo>
cd AINutritionHelp

# 2. Set up environment variables
cp .env.example .env

# Generate a secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Add to .env:
# SECRET_KEY=<generated-key>
# GOOGLE_API_KEY=<your-google-api-key>

# 3. Install dependencies
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Run the application
python run.py

# 5. Open the frontend
# Navigate to: http://localhost:5000
# Or open: frontend/index.html in your browser
```

### Get Google API Key
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Add to `.env`: `GOOGLE_API_KEY=your_key_here`

---

## ✨ Features

### Core Capabilities
- 📱 **Barcode Scanner** - Scan product barcodes to instantly fetch nutrition data
- ✍️ **Manual Entry** - Input nutrition facts manually
- 🤖 **AI Chat Companion** - Conversational nutrition assistant powered by Google Gemini
- ❤️ **Health Analysis** - Evaluates nutritional alignment with your health goals
- 💪 **Fitness Evaluation** - Analyzes products for workout and fitness objectives
- 💰 **Price Analysis** - Assesses value for money and cost-effectiveness
- 🎯 **Personalized Recommendations** - Tailored advice based on your profile
- 📊 **Comprehensive Nutrition Facts** - Displays calories, macros, vitamins, and more

### AI Multi-Agent System
The application uses a sophisticated multi-agent architecture:

- **Health Agent** - Nutritional analysis with pros/cons based on your health profile
- **Fitness Agent** - Workout timing recommendations and fitness alignment
- **Price Agent** - Value assessment and cost analysis
- **Chat Agent** - Natural language Q&A about nutrition and health

---

## 🎯 How to Use

### 1. Create an Account
- Click "Sign Up" to create a new account
- Or use demo credentials if provided

### 2. Complete Your Profile
After signup, complete the 5-step profile setup:
- **Step 1:** Physical profile (height, weight, age, gender)
- **Step 2:** Primary goal (weight loss, muscle gain, maintain, general health)
- **Step 3:** Activity level (sedentary to very active)
- **Step 4:** Diet type (standard, vegetarian, vegan, keto, etc.)
- **Step 5:** Dietary restrictions and allergies

### 3. Scan Products
**Option A: Barcode Scan**
- Upload a photo of the product barcode
- Product info fetched from Open Food Facts database
- Nutrition data automatically populated
- Add price (optional) for value analysis

**Option B: Manual Entry**
- Click "Manual Input" button
- Fill in nutrition facts from the label
- Add item name and price (optional)
- Submit for analysis

### 4. Get AI Analysis
- Click "Get AI Analysis" button
- View comprehensive evaluation:
  - Overall score (0-100)
  - Health alignment analysis
  - Fitness recommendations
  - Price value assessment

### 5. Chat with AI
- Ask questions in the chat interface
- Get personalized nutrition advice
- AI remembers your scanned products
- Use quick action buttons for common questions:
  - "What should I eat before a workout?"
  - "How much protein do I need daily?"
  - "What are healthy snack options?"

---

## 📁 Project Structure

```
AINutritionHelp/
├── backend/
│   ├── api.py                     # Flask REST API
│   ├── auth.py                    # JWT authentication
│   ├── database.py                # SQLite database operations
│   ├── barcode_service.py         # Barcode lookup (Open Food Facts)
│   └── nutrition_agent_service.py # AI agent integration
│
├── frontend/
│   ├── index.html                 # Main application UI
│   ├── app.js                     # Frontend logic
│   ├── styles.css                 # Application styles
│   └── config.js                  # Frontend configuration
│
├── agent/                          # AI Agent System
│   ├── main_agent.py              # Main orchestrator
│   ├── service.py                 # Backend integration
│   ├── models.py                  # Data models
│   ├── health_evaluator.py        # Health analysis agent
│   ├── fitness_evaluator.py       # Fitness evaluation agent
│   ├── price_evaluator.py         # Price analysis agent
│   └── utils/                     # Helper utilities
│       ├── data_parser.py
│       └── response_formatter.py
│
├── config/
│   └── config.py                  # Application configuration
│
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version (for Render deployment)
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore patterns
└── README.md                       # This file
```

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:5000/api`

### Authentication
- `POST /auth/register` - Register new user
  - Body: `{ username, email, password }`
  - Returns: `{ token, user_id, username, email }`

- `POST /auth/login` - Login user
  - Body: `{ username, password }`
  - Returns: `{ token, user: { user_id, username, email, profile } }`

### Profile Management
- `GET /profile` - Get user profile (requires auth)
  - Headers: `Authorization: Bearer <token>`
  - Returns: User profile data

- `POST /profile/setup` - Create/update profile (requires auth)
  - Body: `{ height, current_weight_lbs, gender, age_category, goal_type, activity_level, diet_type, dietary_restrictions }`

- `POST /profile` - Update existing profile (requires auth)
  - Body: Profile fields to update

### Nutrition Scanning & Analysis
- `GET /nutrition/barcode/<barcode>` - Lookup product by barcode (requires auth)
  - Returns: Product nutrition data from Open Food Facts database

- `GET /nutrition/search` - Search for products (requires auth)
  - Query params: `query`, `limit`
  - Returns: List of matching products

- `POST /nutrition/manual` - Submit manual nutrition entry (requires auth)
  - Body: Nutrition facts object
  - Returns: Validated nutrition data

- `POST /agent/evaluate` - Get AI evaluation (requires auth)
  - Body: `{ product: { name, nutrition, price } }`
  - Returns: Complete evaluation from all 3 agents

- `POST /agent/chat` - Chat with AI companion (requires auth)
  - Body: `{ message, product (optional) }`
  - Returns: AI response

### Health Check
- `GET /health` - API status check
  - Returns: `{ status: "healthy" }`

---

## 🤖 Multi-Agent Architecture

### System Design

```
┌─────────────────────────────────────────────────┐
│          Main Nutrition Agent                   │
│         (Google Gemini 2.0)                     │
└──────────┬──────────────────────────────────────┘
           │
    ┌──────┴──────┐
    │  Evaluators │
    └──────┬──────┘
           │
    ┌──────┴────────┬──────────┬──────────┐
    │               │          │          │
┌───▼───┐   ┌──────▼──┐  ┌────▼─────┐  ┌─▼────┐
│Health │   │ Fitness │  │  Price   │  │ Chat │
│Agent  │   │ Agent   │  │  Agent   │  │Agent │
└───────┘   └─────────┘  └──────────┘  └──────┘
```

### Data Flow

1. User scans barcode or enters nutrition data manually
2. Product data fetched from database or validated
3. User requests AI analysis
4. All 3 evaluators run in parallel (asyncio)
5. Results combined into comprehensive evaluation
6. Companion message generated for chat
7. User can ask follow-up questions via chat

### Example Analysis Output

```json
{
  "overall": {
    "score": 85,
    "recommendation": "Great choice for your goals!",
    "recommendation_emoji": "✅"
  },
  "health_analysis": {
    "score": 82,
    "summary": "High protein, low sugar - aligns well with your health goals",
    "pros": ["High protein content", "Low sugar"],
    "cons": ["Moderate sodium levels"]
  },
  "fitness_analysis": {
    "score": 88,
    "summary": "Excellent post-workout option",
    "best_for": "Post-workout recovery",
    "recommendation": "Consume within 30 minutes after exercise"
  },
  "price_analysis": {
    "rating": "Good Value",
    "summary": "$1.99 per serving - reasonable for protein content"
  },
  "companion_message": "Great choice! This has 21g of protein..."
}
```

---

## 💾 Database Schema

### Tables

**users**
- `user_id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `email` (TEXT UNIQUE)
- `password_hash` (TEXT)
- `password_salt` (TEXT)
- `created_at` (TIMESTAMP)
- `last_login` (TIMESTAMP)

**user_profiles**
- `profile_id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER FOREIGN KEY)
- Physical: `height_cm`, `height_feet`, `height_inches`, `current_weight_kg`, `weight_lbs`, `bmi`
- Goals: `goal_type`, `target_weight_kg`, `activity_level`
- Diet: `diet_type`, `dietary_restrictions`, `gender`, `age_category`
- Targets: `daily_calorie_target`, `protein_target_g`, `carbs_target_g`, `fat_target_g`

**nutrition_logs**
- `log_id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER FOREIGN KEY)
- `log_date` (DATE)
- `meal_type` (TEXT)
- `food_name` (TEXT)
- `price` (REAL)
- `nutrition_json` (TEXT)
- Nutrients: `calories`, `protein_g`, `carbs_g`, `fat_g`, `sugar_g`, `sodium_mg`

**weight_history**
- `weight_id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER FOREIGN KEY)
- `weight_kg` (REAL)
- `recorded_at` (TIMESTAMP)

---

## 🛠️ Tech Stack

### Backend
- **Python 3.12+**
- **Flask 3.0+** - REST API framework
- **SQLite3** - Embedded database
- **Google Generative AI** (Gemini 2.0 Flash) - AI/LLM
- **Open Food Facts API** - Product barcode database
- **PyJWT** - JWT authentication
- **Flask-Limiter** - Rate limiting
- **Pydantic** - Data validation

### Frontend
- **HTML5/CSS3/JavaScript** - Vanilla, no frameworks
- **Fetch API** - HTTP requests
- **CSS Grid & Flexbox** - Responsive layouts
- **CSS Variables** - Theming system

### AI
- **Google Gemini 2.0 Flash** - Multi-agent reasoning
- **Parallel execution** - Asyncio for concurrent agent calls
- **Context-aware conversations** - Maintains chat history
- **Structured outputs** - JSON parsing for consistent results

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required
SECRET_KEY=your_secret_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional
FLASK_ENV=development
PORT=5000
```

### Frontend Configuration (frontend/config.js)

```javascript
window.BalanceBotConfig = {
    API_URL: 'http://localhost:5000/api',
    DEBUG: false
};
```

---

## 🔍 Troubleshooting

### Backend Won't Start

**Error:** Module not found

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### AI Analysis Fails

**Error:** "Nutrition agent not available"

**Solution:**
1. Check `.env` has valid `GOOGLE_API_KEY`
2. Verify API key at: https://aistudio.google.com/apikey
3. Restart the backend: `python run.py`

### CORS Errors

**Error:** Cross-origin request blocked

**Solution:**
- Ensure backend is running on port 5000
- Check `frontend/config.js` has correct API_URL
- For production, configure proper CORS headers

---

## 🚀 Deployment

### Important Notes
- **Database is periodically reset** - This is an educational project
- User data may be deleted without notice
- Not intended for production use with real user data

### Local Deployment
```bash
python run.py
# Access at: http://localhost:5000
```

### Production Considerations
If deploying for demonstration:
1. Set `FLASK_ENV=production` in `.env`
2. Use a strong `SECRET_KEY`
3. Consider PostgreSQL instead of SQLite for multi-user
4. Set up proper HTTPS/SSL
5. Configure CORS properly
6. Add rate limiting

---

## 📊 Performance

- **Barcode Lookup:** 1-2 seconds (depends on API response)
- **AI Evaluation (3 agents):** 2-4 seconds (parallel execution)
- **Chat Response:** 1-2 seconds
- **Manual Entry:** Instant

---

## 🎓 Educational Purpose

This project demonstrates:
- Full-stack web development (Flask + Vanilla JS)
- RESTful API design
- JWT authentication & security
- Multi-agent AI systems
- External API integration (Open Food Facts)
- Barcode scanning & data processing
- Responsive web design
- Database design and operations
- Rate limiting & CORS configuration

**Not suitable for:**
- Medical or nutritional advice
- Production health applications
- Storing real user health data
- Making dietary decisions

---

## 📄 License

MIT License - See LICENSE file for details

**Disclaimer:** This software is provided "as is" without warranty of any kind. Use at your own risk.

---

## 🤝 Contributing

This is an educational project. Contributions for learning purposes are welcome:
- Bug fixes
- UI/UX improvements
- Documentation enhancements
- Code refactoring
- Adding tests

---

## 📞 Support

For issues or questions about the codebase:
1. Check the troubleshooting section above
2. Review backend logs: `python run.py`
3. Check browser console (F12) for frontend errors
4. Verify API health: `curl http://localhost:5000/api/health`

---

**Made with ❤️ as a computer science educational project**

*Remember: Always consult qualified healthcare professionals for actual nutrition and dietary advice.*
