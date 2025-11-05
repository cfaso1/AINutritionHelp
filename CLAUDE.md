# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Quick Start Commands

### Setup
```bash
# Install dependencies (requires Python 3.12+)
pip install -r requirements.txt

# Set up Google API key for Gemini
# Edit agent/.env and add: GOOGLE_API_KEY=your_key_here
```

### Development
```bash
# Start the API server (main entry point)
python run.py

# Or directly run the API
python backend/api.py

# Test the agent system
python -c "from agent import get_agent; print(get_agent())"

# Run agent demo (shows full evaluation pipeline)
python agent/demo.py

# Using Google ADK (for testing agent outside web)
./venv/bin/adk run agent
```

### Frontend
- Open `frontend/index.html` in browser
- Demo account: `demo_user` / `demo123`

---

## 📐 Architecture Overview

### Three-Tier System

**1. Frontend Layer** (`frontend/`)
- Vanilla HTML/CSS/JS application (index.html, app.js, styles.css)
- No frameworks; uses Fetch API to communicate with backend
- Real-time chat interface for AI companion

**2. Backend API** (`backend/`)
- Flask REST API (`api.py`) - main entry point
- Routes handle: auth, profiles, barcode scanning, AI chat
- SQLite database integration (`database.py`)
- Image OCR pipeline (`ingest/`) for manual nutrition data extraction

**3. AI Agent System** (`agent/`)
- Multi-evaluator architecture using Google Gemini 2.0-flash
- Coordinate operations: barcode scanning, health/fitness/price analysis, chat
- Async processing with parallel evaluator execution

### Data Flow for Product Evaluation
```
User scans item
    ↓
Backend receives barcode
    ↓
Agent: scan_barcode() → fetch product data
    ↓
Agent: evaluate_product() → run 3 evaluators in parallel
    ├─ HealthEvaluator (nutritional alignment)
    ├─ FitnessEvaluator (workout suitability)
    └─ PriceEvaluator (value for money)
    ↓
Companion message generated
    ↓
Frontend displays results + chat message
```

---

## 🏗️ Key Components

### Backend Structure
- **api.py** - Flask app, REST endpoints, request routing
- **database.py** - SQLite schema, user/profile/weight tracking
- **nutrition_agent_service.py** - Wrapper to integrate agent with Flask
- **ingest/** - OCR pipeline for extracting nutrition facts from images
  - `ocr_reader.py` - Tesseract OCR wrapper
  - `nutrition_parser.py` - Parse OCR text into structured data
  - `clarify.py` - AI-powered clarification of parsed data

### Agent System Structure
- **main_agent.py** - NutritionAgent orchestrator class
- **models.py** - Pydantic models: Product, UserProfile
- **health_evaluator.py** - Nutritional analysis (macros, micronutrients)
- **fitness_evaluator.py** - Workout timing and fitness recommendations
- **price_evaluator.py** - Cost analysis and value comparisons
- **utils/**
  - `data_parser.py` - Nutrition data normalization and macro calculation
  - `response_formatter.py` - Format evaluations for frontend display
- **service.py** - Backend integration layer (async wrapper for Flask)

### Frontend Structure
- **index.html** - Main HTML structure and UI components
- **app.js** - All JavaScript logic including:
  - Login/registration logic
  - Profile settings form
  - Nutrition image upload with OCR
  - Real-time chat interface
  - Fetch API calls to backend
- **styles.css** - Application styling and animations

---

## 🔑 Important Integration Points

### API Endpoints (Used by Frontend)
```
POST /api/auth/register              # User registration
POST /api/auth/login                 # User login
GET  /api/profile                    # Get user profile
PUT  /api/profile                    # Update profile
POST /api/profile/setup              # Initial profile setup
POST /api/nutrition/ocr              # Upload nutrition label image (OCR)
POST /api/nutrition/manual           # Manual nutrition entry
POST /api/nutrition/clarify          # Clarify/correct OCR results
POST /api/agent/evaluate             # Get 3-evaluator analysis
POST /api/agent/chat                 # AI chat endpoint
POST /api/weight                     # Log weight
GET  /api/weight/history             # Get weight tracking data
GET  /api/health                     # Health check
```

### Environment Setup
- **Root .env** - Set `GOOGLE_API_KEY` here (loaded by `run.py`)
- **agent/.env** - Agent-specific keys (Gemini API key)
- Keys are loaded via `python-dotenv` at startup

### Database
- **SQLite file**: Likely `nutrition.db` (created by `database.py` on first run)
- Tables: users, user_profiles, nutrition_logs, weight_history
- Access via functions in `database.py` (not direct SQL queries in API)

---

## 🔄 Common Development Tasks

### Adding New Evaluator
1. Create new file: `agent/new_evaluator.py`
2. Implement class with `async def evaluate(product, user_profile) -> Dict` method
3. Import in `main_agent.py`
4. Add to `NutritionAgent.__init__()` and `evaluate_product()`
5. Update response formatter to include new results

### Adding New API Endpoint
1. Define route in `backend/api.py` using `@app.route()`
2. Extract JSON data with `request.get_json()`
3. Call agent service or database function
4. Return JSON response with `jsonify()`
5. Update frontend fetch calls in `frontend/app.js`

### Modifying Chat Behavior
- Chat logic: `agent/main_agent.py` - `chat()` method
- Response generation uses Gemini API with system prompt
- Context includes user profile + recently scanned products
- Frontend sends messages to `/api/agent/chat` endpoint

### Updating Database Schema
1. Modify schema in `database.py`
2. Add migration function (see existing `migrate_database()` pattern)
3. Call migration in `api.py` startup
4. Update corresponding database helper functions

---

## ⚡ Performance Considerations

- **Parallel Evaluations**: Health, fitness, and price evaluators run concurrently via `asyncio.gather()`
- **Gemini API**: Uses 2.0-flash model (fast, cheaper than pro variants)
- **Barcode Lookup**: Attempts multiple APIs; fails gracefully with mock data
- **Frontend**: No build process needed; single HTML file loads instantly
- **Caching**: No explicit caching currently; consider for barcode lookups

---

## 🧪 Testing

### Test Barcodes (Mock Products)
```
722252601025  - Quest Protein Bar (high protein, low sugar)
012000161551  - Coca-Cola (high sugar)
016000275683  - Cheerios (moderate nutrition)
078000113464  - Gatorade (sports drink)
028400047685  - Cheez-It (snack)
```

### Manual Testing Flow
1. Run `python run.py`
2. Open `frontend/index.html` in browser
3. Login with demo_user / demo123
4. Set profile (health goals, activity level, targets)
5. Upload nutrition label image or enter manually
6. Check evaluation results
7. Chat with AI for follow-up questions

### Agent Testing
```bash
python -c "
import asyncio
from agent import get_agent
from agent.models import UserProfile

async def test():
    agent = get_agent()
    product = await agent.scan_barcode('722252601025')
    profile = UserProfile(health_goals='muscle building')
    result = await agent.evaluate_product(product, profile)
    print(result)

asyncio.run(test())
"
```

---

## 🐛 Debugging Tips

### Check API Health
```bash
curl http://localhost:5000/api/health
```

### View Agent Initialization
```bash
python -c "from agent import get_agent; print(get_agent())"
```

### Inspect Database
```bash
sqlite3 nutrition.db ".tables"
sqlite3 nutrition.db "SELECT * FROM users;"
```

### Enable Flask Debug Logging
- `run.py` already runs with `debug=True`
- Check console output for route handling and errors

### Frontend Console Errors
- Open browser DevTools (F12)
- Check Console and Network tabs
- Look for CORS errors or failed fetch calls

---

## 📚 Key Files to Know

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `backend/api.py` | Main Flask app | app, routes, error handling |
| `backend/database.py` | Database operations | init_database, create_user, get_user_profile |
| `backend/nutrition_agent_service.py` | Agent integration | get_nutrition_agent_service, run_async |
| `agent/main_agent.py` | AI orchestration | NutritionAgent, evaluate_product, chat |
| `agent/health_evaluator.py` | Nutritional analysis | HealthEvaluator.evaluate |
| `agent/fitness_evaluator.py` | Fitness evaluation | FitnessEvaluator.evaluate |
| `agent/price_evaluator.py` | Price analysis | PriceEvaluator.evaluate |
| `frontend/index.html` | Web UI structure | HTML markup and components |
| `frontend/app.js` | Frontend logic | Auth, chat, nutrition scanning |
| `frontend/styles.css` | Application styles | CSS styling and animations |

---

## 🔐 API Key Management

- **Google API Key** required for Gemini 2.0-flash
- Create in `.env` at root (loaded by run.py) or `agent/.env`
- Get key: https://aistudio.google.com/apikey
- Key in committed `.env` file is for demo purposes (not secret management)

---

## 🚨 Common Issues & Solutions

| Issue | Cause | Fix |
|-------|-------|-----|
| "Nutrition agent not available" | Missing Google API key | Add GOOGLE_API_KEY to .env |
| Chat shows "encountered an error" | API key invalid or missing | Verify key in agent/.env |
| Frontend can't connect to API | Backend not running | Run `python run.py` |
| Port 5000 already in use | Another process using port | Kill process or change port in run.py |
| OCR not working | Tesseract not installed | Install tesseract-ocr system package |

---

## 📖 Code Style & Patterns

- **Async/await**: Agent uses asyncio for I/O operations
- **Type hints**: Pydantic models for validation; type hints in function signatures
- **Error handling**: Try/except blocks with fallback analyses
- **Singleton pattern**: Agent initialized once per service
- **Response formats**: JSON with consistent structure (product, health_analysis, fitness_analysis, etc.)

