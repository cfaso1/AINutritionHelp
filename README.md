# 🍎 BalanceBot AI

Scan products, get AI-powered nutrition analysis, and reach your health goals with personalized recommendations from a multi-agent AI system.

**Production-Ready** ✅ - Secure authentication, multi-user support, Docker deployment, and enterprise-grade security.

*Note: This Full-stack AI powered web app was created during the KnightHacksVIII 36 hour hackathon and later polished for production*

---

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone and setup environment
git clone <your-repo>
cd AINutritionHelp
cp .env.example .env

# 2. Generate secret key and configure
python3 -c "import secrets; print(secrets.token_hex(32))"
# Add to .env: SECRET_KEY=<generated-key>
# Add to .env: GOOGLE_API_KEY=<your-google-api-key>

# 3. Install dependencies
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Run the application
python run.py

# 5. Open frontend
# Open: frontend/index.html in your browser
```

### Docker Deployment (Recommended)

```bash
# Quick start with Docker
cp .env.example .env
# Edit .env with your values
docker-compose up -d --build
```

📚 **For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**
📚 **For production readiness guide, see [PRODUCTION_READY.md](PRODUCTION_READY.md)**

---

## ✨ Features

### Core Capabilities
- 🔍 **Item Scanner** - Scan nutrition facts or upload images
- 🤖 **AI Chat Companion** - Conversational nutrition assistant powered by Gemini 2.0
- ❤️ **Health Evaluator** - Analyzes nutrition alignment with health goals
- 💪 **Fitness Evaluator** - Evaluates products for fitness objectives
- 💰 **Price Evaluator** - Assesses value for money
- 💬 **Live Chat Interface** - Real-time AI conversations about nutrition
- 🎯 **Personalized Recommendations** - Based on your profile and goals

### AI Multi-Agent System
- **Health Agent** - Nutritional analysis with pros/cons
- **Fitness Agent** - Workout timing and recommendations
- **Price Agent** - Value assessment and alternatives
- **Chat Agent** - Natural language Q&A about nutrition

---

## 📁 Project Structure

```
AINutritionHelp/
├── backend/
│   ├── api.py                     # REST API (includes chat endpoint)
│   ├── database.py                # SQLite database
│   ├── nutrition_agent_service.py # Agent integration wrapper
│   └── ingest/                    # OCR and nutrition data extraction
│
├── frontend/
│   ├── index.html                 # Main app with AI chat interface
│   ├── app.js                     # Frontend JavaScript logic
│   └── styles.css                 # Application styles
│
├── agent/                          # AI Agent System
│   ├── main_agent.py              # Main orchestrator
│   ├── service.py                 # Backend integration layer
│   ├── models.py                  # Product & UserProfile models
│   ├── health_evaluator.py        # Health analysis agent
│   ├── fitness_evaluator.py       # Fitness evaluation agent
│   ├── price_evaluator.py         # Price analysis agent
│   ├── adk_agent.py               # Google ADK integration
│   └── utils/                     # Helper utilities
│       ├── data_parser.py
│       └── response_formatter.py
│
└── requirements.txt                # Python dependencies
```

---

## 🎯 How to Use

### 1. **Login**
- Use demo account: `demo_user` / `demo123`
- Or create your own account

### 2. **Set Your Profile**
Navigate to Settings and configure:
- Personal info (height, weight, goals)
- Activity level
- Dietary restrictions
- Daily targets (calories, protein, etc.)

### 3. **Scan Products**
- **Enter data manually** (e.g., `protein: `)
- **Upload data image** - automatically extracts data
- View product information and nutrition facts

### 4. **Chat with AI**
- Ask questions in the chat interface
- Get personalized nutrition advice
- AI remembers your scanned products
- Use quick action buttons for common questions

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:5000`

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile

### Nutrition Scanning & Analysis
- `POST /nutrition/ocr` - Upload nutrition label image (OCR)
- `POST /nutrition/manual` - Submit manual nutrition entry
- `POST /nutrition/clarify` - Clarify/correct OCR results
- `POST /agent/evaluate` - Get AI evaluation (3 agents)
- `POST /agent/chat` - Chat with AI companion ✨

### Weight Tracking
- `POST /weight` - Log weight
- `GET /weight/history` - Get weight history

### Health Check
- `GET /health` - API status

---

## 💬 AI Chat Interface

### What It Does
The chat interface provides a conversational AI companion that:
- Automatically sends analysis results when you scan products
- Answers nutrition and fitness questions
- Provides context-aware advice based on your profile
- Remembers recently scanned products

### How It Works

**Auto-Trigger on Scan:**
```
User scans item → AI analyzes product →
Companion message appears in chat automatically
```

**Manual Chat:**
```
User types question → AI responds with personalized advice
```

**Quick Actions:**
- 💪 "What should I eat before a workout?"
- 🥗 "How much protein do I need daily?"
- 🍎 "What are healthy snack options?"

### Example Conversation
```
🤖 Hey! I just looked at the Quest Protein Bar you scanned.
   With 21g protein and only 1g sugar, this is an excellent
   choice for your muscle building goals!

   Overall Score: 85/100 ✅
   Best time: Post-workout

👤 Is this good for me?

🤖 Absolutely! Based on your moderately active lifestyle and
   protein target of 100g/day, this bar provides 21% of your
   daily protein needs. Perfect as a post-workout snack!
```

---


## 🔧 Configuration

### Required: Google API Key

The agent system uses **Google Gemini 2.0-flash** 

**Create `agent/.env`:**
```env
GOOGLE_API_KEY=your_google_api_key_here
```

**Get API Key:**
1. Go to https://aistudio.google.com/apikey
2. Create a new API key
3. Add to `agent/.env`

---

## 🤖 Multi-Agent Architecture

### Agent System (Google Gemini 2.0)

```
┌─────────────────────────────────────────────────┐
│          Main Nutrition Agent                   │
│         (NutritionAgent class)                  │
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
```
1. User scans item
2. Product info retrieved
3. All 3 evaluators run in parallel (asyncio)
4. Results combined
5. Companion message generated
6. Message sent to chat interface
7. User can ask follow-up questions
```

---

## 💾 Database Schema

### Tables

**users**
- user_id, username, email
- password_hash, password_salt
- created_at, last_login

**user_profiles**
- Personal: height_cm, current_weight_kg, bmi
- Goals: goal_type, target_weight_kg, activity_level
- Diet: diet_type, allergies, dietary_restrictions
- Targets: daily_calorie_target, protein_target_g, carbs_target_g, fat_target_g

**nutrition_logs**
- log_date, meal_type, food_name, price
- nutrition_json, calories, protein_g, carbs_g, fat_g

**weight_history**
- weight_id, user_id, weight_kg, recorded_at

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- Flask 3.0.0 (REST API)
- SQLite3
- Google Generative AI SDK (Gemini 2.0-flash)
- Tesseract OCR + OpenCV (nutrition label extraction)

**Frontend:**
- Vanilla HTML5/CSS3/JavaScript
- No frameworks (lightweight, fast)
- Modern CSS (flexbox, grid, animations)
- Fetch API for HTTP requests

**AI:**
- Google Gemini 2.0-flash (via genai SDK)
- Multi-agent system with parallel execution
- Context-aware conversations

---

## 🔍 Troubleshooting

### "Nutrition agent not available" Error

**Cause:** Missing or invalid Google API key

**Fix:**
```bash
# 1. Check if .env exists
cd agent
ls -la .env

# 2. If missing, create it:
echo "GOOGLE_API_KEY=your_key_here" > .env

# 3. Verify it's loaded
cat .env

# 4. Restart the backend
cd ..
python backend/api.py
```

### Chat Shows "Sorry, I encountered an error"

**Causes:**
1. Google API key not set
2. API key invalid/expired
3. Network connection issue
4. Agent service not initialized

**Debug Steps:**
```bash
# Test the agent directly
cd agent
python -c "from main_agent import get_agent; print(get_agent())"

# Check API key is valid
# Go to: https://aistudio.google.com/apikey

# Check backend logs
# Look for errors when starting api.py
```

### Frontend Can't Connect to API

**Check:**
```bash
# 1. Is backend running?
curl http://localhost:5000/api/health

# 2. Check backend is on port 5000
# Should see: * Running on http://0.0.0.0:5000

# 3. Check browser console (F12) for CORS errors
```

---

## 🚀 Running with Google ADK

The agent also supports Google Agent Development Kit:

```bash
# Start ADK agent
./venv/bin/adk run agent

```

This is useful for testing the agent outside the web interface.

---

## 📊 Performance

- **Agent Response Time:** 2-4 seconds (all 3 agents in parallel)
- **Chat Response Time:** 1-2 seconds
- **Image Detection:** 1-2 seconds

---

## 🎯 Roadmap

- [ ] Save chat history to database
- [ ] Add message timestamps
- [ ] Export chat conversations
- [ ] Voice input for chat
- [ ] Meal planning suggestions
- [ ] Recipe recommendations
- [ ] Social features (meal sharing)

---


## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Mobile app (API is ready)
- Recipe engine
- Social features
- Multi-language support
- Fitness tracker integration

---

## 📞 Support

**Check the logs:**
```bash
# Backend logs
python backend/api.py
# Look for errors on startup

# Check API health
curl http://localhost:5000/api/health
```

---

**Made with ❤️ for better nutrition tracking**
