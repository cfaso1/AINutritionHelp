# 🍎 AI Nutrition Help

Scan product barcodes, get AI-powered nutrition analysis, and reach your health goals with personalized recommendations from a multi-agent AI system.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cd agent
nano .env  # Add: GOOGLE_API_KEY=your_key_here

# 3. Start the backend
cd ..
python backend/api_simple.py

# 4. Open the frontend
# Open: frontend/nutriscan_zen.html in your browser
```

**Demo Login:** `demo_user` / `demo123`

---

## ✨ Features

### Core Capabilities
- 🔍 **Barcode Scanner** - Scan product barcodes or upload images
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
│   ├── api_simple.py              # REST API (includes chat endpoint)
│   ├── database.py                # SQLite database
│   ├── nutrition_agent_service.py # Agent integration wrapper
│   ├── barcode_detector.py        # Image barcode extraction
│   └── uploads/                   # Uploaded images
│
├── frontend/
│   ├── nutriscan_zen.html         # Main app with AI chat interface
│   └── demo.html                  # Legacy version
│
├── agent/                          # AI Agent System (NEW)
│   ├── main_agent.py              # Main orchestrator
│   ├── service.py                 # Backend integration layer
│   ├── models.py                  # Product & UserProfile models
│   ├── barcode_service.py         # Barcode API integration
│   ├── health_evaluator.py        # Health analysis agent
│   ├── fitness_evaluator.py       # Fitness evaluation agent
│   ├── price_evaluator.py         # Price analysis agent
│   ├── agent.py                   # Google ADK integration
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
- **Enter barcode manually** (e.g., `722252601025`)
- **Upload barcode image** - automatically extracts barcode
- View product information and nutrition facts

### 4. **Get AI Analysis**
- Click "Get AI Analysis" button
- View comprehensive evaluation:
  - Health score and recommendations
  - Fitness alignment and timing
  - Price assessment
- **AI companion message appears in chat automatically!**

### 5. **Chat with AI**
- Ask questions in the chat interface
- Get personalized nutrition advice
- AI remembers your scanned products
- Use quick action buttons for common questions

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:5000/api`

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile

### Barcode & Analysis
- `POST /barcode/scan` - Scan barcode number
- `POST /barcode/image` - Upload barcode image
- `POST /agent/evaluate` - Get AI evaluation (3 agents)
- `POST /agent/chat` - Chat with AI companion ✨ **NEW**

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
User scans barcode → AI analyzes product →
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

## 🧪 Test Barcodes

Try these sample products:

| Product | Barcode | Notes |
|---------|---------|-------|
| Quest Protein Bar | `722252601025` | High protein, low sugar ✅ |
| Coca-Cola Classic | `012000161551` | High sugar ⚠️ |
| Gatorade | `078000113464` | Sports drink |
| Cheerios | `016000275683` | Breakfast cereal |

---

## 🔧 Configuration

### Required: Google API Key

The agent system uses **Google Gemini 2.0-flash** (not Anthropic Claude).

**Create `agent/.env`:**
```env
GOOGLE_API_KEY=your_google_api_key_here
BARCODE_LOOKUP_API_KEY=your_barcode_api_key  # Optional
```

**Get API Key:**
1. Go to https://aistudio.google.com/apikey
2. Create a new API key
3. Add to `agent/.env`

### Optional: Barcode Lookup API
For real product data, get a key from:
- https://www.barcodelookup.com/api

Without this, the app uses mock data for test barcodes.

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
1. User scans barcode
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
- OpenCV + pyzbar (barcode detection)

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
python backend/api_simple.py
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
# Look for errors when starting api_simple.py
```

### Barcode Image Upload Not Working

**Cause:** Missing system dependencies

**Fix:**
```bash
# Ubuntu/Debian:
sudo apt-get install libzbar0

# macOS:
brew install zbar

# Then reinstall Python package:
pip install pyzbar
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

# Then interact via CLI:
> Can you scan barcode 722252601025?
> Evaluate barcode 722252601025 for muscle building
```

This is useful for testing the agent outside the web interface.

---

## 📊 Performance

- **Agent Response Time:** 2-4 seconds (all 3 agents in parallel)
- **Chat Response Time:** 1-2 seconds
- **Barcode Lookup:** <1 second
- **Image Barcode Detection:** 1-2 seconds

---

## 🎯 Roadmap

- [ ] Save chat history to database
- [ ] Support markdown formatting in chat
- [ ] Add message timestamps
- [ ] Export chat conversations
- [ ] Voice input for chat
- [ ] Real-time camera barcode scanning
- [ ] Meal planning suggestions
- [ ] Recipe recommendations
- [ ] Social features (meal sharing)

---

## 📝 Development Notes

### Recent Changes (v2.0)
- ✅ Migrated from Anthropic Claude to Google Gemini
- ✅ Added AI chat interface (replaced "Example Barcodes")
- ✅ Integrated chat with barcode scanning
- ✅ Auto-trigger chat messages on product analysis
- ✅ Added quick action buttons
- ✅ Improved UI/UX with animations

### Migration Summary
The codebase was refactored to:
1. Use Google Gemini instead of Claude
2. Consolidate agent code into `agent/` directory
3. Add conversational chat capability
4. Improve frontend with modern chat UI

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
python backend/api_simple.py
# Look for errors on startup

# Check API health
curl http://localhost:5000/api/health
```

**Common Issues:**
1. ❌ "Nutrition agent not available" → Add Google API key to `agent/.env`
2. ❌ Chat not working → Check browser console (F12)
3. ❌ Barcode image upload fails → Install libzbar
4. ❌ Database errors → Delete `backend/nutrition_app.db` and restart

---

**Made with ❤️ for better nutrition tracking**
