# AI Nutrition Help - Hackathon Demo

Scan nutrition labels, extract data with OCR, and get AI-powered health recommendations!

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python run.py
```

### 3. Open the Demo
Open `demo.html` in your web browser!

**That's it!** No authentication, no configuration needed.

---

## 📁 Project Structure

```
AINutritionHelp/
├── run.py                      # START HERE - Main entry point
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── backend/                    # Backend Code
│   ├── api_simple.py          # REST API (no authentication)
│   ├── database.py            # SQLite database functions
│   ├── nutrition_reader.py   # OCR nutrition label scanner
│   ├── ai_model.py            # Custom AI model integration
│   ├── nutrition_json.json    # Sample nutrition data format
│   ├── uploads/               # Uploaded images (auto-created)
│   └── nutrition_app.db       # SQLite database (auto-created)
│
├── frontend/                   # Frontend Code
│   └── demo.html              # Web interface with drag & drop
│
└── docs/                       # Documentation
    ├── README.md              # This file - full documentation
    ├── SETUP.md               # Quick setup guide
    └── PROJECT_STRUCTURE.md   # Detailed structure info
```

---

## 🎯 Features

### ✅ What Works Now:
- **Upload nutrition label images** (drag & drop)
- **OCR scanning** - Extract nutrition data automatically
- **Nutrition logging** - Save meals to database
- **Daily stats** - Track calories, protein, carbs, fat
- **Weight tracking** - Log and view weight history
- **User profiles** - Store health goals and preferences
- **Demo AI analysis** - Placeholder for AI integration

### 🤖 AI Integration (Custom Model):
To integrate your custom trained AI model:
1. Train your nutrition analysis model
2. Save it to a file (e.g., `model.pkl`, `model.h5`, `model.pth`)
3. Edit `backend/ai_model.py` to load and use your model
4. The API will automatically use your model when available!

See `backend/ai_model.py` for implementation examples with TensorFlow, PyTorch, and scikit-learn.

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:5000/api`

**No authentication required - all endpoints use demo user (ID: 1)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update user profile |
| POST | `/scan` | Upload & scan nutrition label |
| POST | `/analyze` | Get AI nutrition analysis |
| POST | `/log` | Save nutrition to log |
| GET | `/logs` | Get today's nutrition logs |
| POST | `/weight` | Log weight entry |
| GET | `/weight/history` | Get weight history |

---

## 💻 Frontend Integration

### Using with React/Vue/vanilla JS:

```javascript
const API_URL = 'http://localhost:5000/api';

// Scan nutrition label
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch(`${API_URL}/scan`, {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.nutrition_data);
```

### Example Response:
```json
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
      "protein": { "amount_g": "12" },
      "fat": { "total_g": "8", "saturated_g": "3" },
      "carbohydrates": { "total_g": "25", "fiber_g": "3" }
    }
  }
}
```

---

## 🛠️ How It Works

```
User uploads image → OCR extraction → Structured JSON → AI Analysis → Database storage
```

1. **Upload**: User uploads nutrition label photo via `frontend/demo.html`
2. **OCR**: `backend/nutrition_reader.py` uses Tesseract to extract text
3. **Parse**: Regex patterns extract structured nutrition data
4. **Analyze**: (Optional) Send to AI for personalized recommendations
5. **Store**: Save to SQLite database via `backend/database.py`
6. **Display**: Show stats and history in web interface

---

## 📊 Database Schema

### Users Table
- `user_id`, `username`, `email`, `password_hash`, `password_salt`

### User Profiles
- Personal info: DOB, gender, height, weight
- Goals: goal_type, target_weight, activity_level
- Diet: diet_type, allergies, dietary_restrictions
- Targets: daily calories, protein, carbs, fat

### Nutrition Logs
- `log_id`, `user_id`, `food_name`, `meal_type`
- `nutrition_json` (full nutrition data)
- Quick fields: calories, protein, fat, carbs
- `image_path`, `notes`, timestamps

### Weight History
- `weight_id`, `user_id`, `weight_kg`, `recorded_at`, `notes`

---

## 🎓 For Development

### Run Database Examples:
```bash
./venv/bin/python example_usage.py
```

### Test OCR Scanner:
```bash
./venv/bin/python nutrition_reader.py path/to/label.jpg
```

### Test API:
```bash
# Check health
curl http://localhost:5000/api/health

# Get profile
curl http://localhost:5000/api/profile

# Get logs
curl http://localhost:5000/api/logs
```

---

## ⚠️ Important Notes

- **For demo purposes only** - No authentication/security
- All requests use a single demo user (ID: 1)
- Server runs on `http://localhost:5000`
- CORS enabled for all origins
- Max upload size: 16MB

---

## 📦 Dependencies

- **Flask** - Web framework
- **flask-cors** - CORS handling
- **pytesseract** - OCR engine
- **Pillow** - Image processing
- **anthropic** - AI API (optional)
- **sqlite3** - Database (built-in)

---

## 🏆 Hackathon Tips

1. **Quick Demo**: Just open `frontend/demo.html` and it works!
2. **Customize UI**: Edit `frontend/demo.html` for your branding
3. **Add Your AI Model**: Edit `backend/ai_model.py` to integrate your trained model
4. **Frontend Integration**: Copy API calls from `frontend/demo.html`
5. **Extend Features**: Add meal recommendations, streak tracking, etc.

---

## 🧠 Training Your Custom AI Model

Your AI model should:
1. **Input**: Nutrition data (JSON) + User profile (goals, diet type, etc.)
2. **Output**: Personalized nutrition analysis and recommendations

### Data Format:

**Input nutrition_data:**
```python
{
    'calories': {'total': '210', 'from_fat': '70'},
    'macronutrients': {
        'protein': {'amount_g': '12'},
        'fat': {'total_g': '8'},
        'carbohydrates': {'total_g': '25'}
    },
    'micronutrients': {...}
}
```

**Input user_profile:**
```python
{
    'goal_type': 'muscle_gain',
    'diet_type': 'high_protein',
    'daily_calorie_target': 2500,
    'daily_protein_target_g': 150,
    'allergies': 'peanuts',
    'dietary_restrictions': 'none'
}
```

**Expected output:** String with personalized analysis

### Integration Steps:
1. Train your model on nutrition datasets
2. Save trained model: `model.save('my_model.pkl')`
3. Edit `backend/ai_model.py`:
   - Update `__init__()` to load your model
   - Update `analyze()` to use your model for predictions
   - Implement `_prepare_features()` if needed
4. Restart API server - it automatically detects your model!

See `backend/ai_model.py` for detailed code examples and templates.

---

## 🐛 Troubleshooting

**"Network Error: Failed to fetch"**
- Make sure API server is running: `python run.py`
- Check server is on port 5000: `curl http://localhost:5000/api/health`

**"Tesseract not found"**
- Install Tesseract OCR:
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

**"Module not found"**
- Install dependencies: `./venv/bin/pip install -r requirements.txt`

---

## 📝 License

MIT - Free for hackathons and personal projects!

---

**Good luck with your hackathon! 🚀**
