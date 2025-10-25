# AI Nutrition Help - Hackathon Demo

Scan nutrition labels, extract data with OCR, and get AI-powered health recommendations!

## 🚀 Quick Start

```bash
# 1. Install dependencies
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 2. Start the server
python run.py

# 3. Open the demo
Open frontend/demo.html in your browser!
```

**That's it!** No authentication, no configuration needed.

---

## 📁 Project Structure

```
AINutritionHelp/
├── run.py                    # Start server (use this!)
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── backend/                 # Backend code
│   ├── api_simple.py        # REST API (no auth)
│   ├── database.py          # SQLite database
│   ├── nutrition_reader.py  # OCR scanner
│   └── ai_model.py          # YOUR AI model integration
├── frontend/                # Frontend code
│   └── demo.html            # Web interface
└── docs/                    # Documentation
    ├── README.md            # Full documentation
    └── SETUP.md             # Quick setup guide
```

---

## 🎯 Features

- ✅ **Upload nutrition labels** - Drag & drop images
- ✅ **OCR scanning** - Extract nutrition data automatically
- ✅ **Nutrition logging** - Save meals to database
- ✅ **Daily stats** - Track calories, protein, carbs, fat
- ✅ **Weight tracking** - Log and view weight history
- ✅ **User profiles** - Store health goals
- ✅ **AI-ready** - Plug in your custom model!

---

## 🤖 Add Your Custom AI Model

Edit `backend/ai_model.py` to integrate your trained nutrition analysis model:

```python
class NutritionAI:
    def __init__(self, model_path=None):
        # Load your model
        self.model = load_model(model_path)

    def analyze(self, nutrition_data, user_profile):
        # Use your model
        prediction = self.model.predict(nutrition_data, user_profile)
        return prediction
```

The API automatically detects and uses your model!

**See [docs/README.md](docs/README.md) for complete AI integration guide.**

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:5000/api`

**No authentication required!**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update profile |
| POST | `/scan` | Scan nutrition label |
| POST | `/analyze` | Get AI analysis |
| POST | `/log` | Save to log |
| GET | `/logs` | View logs |
| POST | `/weight` | Log weight |
| GET | `/weight/history` | View history |

---

## 💻 Frontend Integration

```javascript
const API_URL = 'http://localhost:5000/api';

// Upload and scan
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch(`${API_URL}/scan`, {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.nutrition_data);
```

---

## 🛠️ Development

```bash
# Test database
./venv/bin/python example_usage.py

# Test OCR
./venv/bin/python -m backend.nutrition_reader image.jpg

# Test AI model
./venv/bin/python -m backend.ai_model
```

---

## ⚠️ Important

- **Demo purposes only** - No security
- Single demo user (ID: 1)
- CORS enabled for all origins
- Perfect for hackathons!

---

## 📖 Full Documentation

- **[docs/README.md](docs/README.md)** - Complete documentation
- **[docs/SETUP.md](docs/SETUP.md)** - Quick setup guide
- **[backend/ai_model.py](backend/ai_model.py)** - AI integration examples

---

**Good luck with your hackathon! 🚀**
