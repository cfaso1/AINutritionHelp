# AI Nutrition Help - Hackathon Demo

Scan nutrition labels, extract data with OCR, and get AI-powered health recommendations!

## Quick Start (3 Steps)

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
Open `frontend/demo.html` in your web browser!

**That's it!** No authentication, no configuration needed.

---

## Features

- Upload nutrition label images (drag & drop)
- OCR scanning - Extract nutrition data automatically
- Nutrition logging - Save meals to database
- Daily stats - Track calories, protein, carbs, fat
- Weight tracking - Log and view weight history
- User profiles - Store health goals and preferences
- Demo AI analysis - Placeholder for AI integration

## Project Structure

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
    ├── README.md              # Full documentation
    ├── SETUP.md               # Quick setup guide
    └── PROJECT_STRUCTURE.md   # Detailed structure info
```

## API Endpoints

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

## Custom AI Model Integration

To integrate your custom trained AI model:
1. Train your nutrition analysis model
2. Save it to a file (e.g., `model.pkl`, `model.h5`, `model.pth`)
3. Edit `backend/ai_model.py` to load and use your model
4. The API will automatically use your model when available!

See `backend/ai_model.py` for implementation examples with TensorFlow, PyTorch, and scikit-learn.

## Quick Test

```bash
# Test API
curl http://localhost:5000/api/health

# Get profile
curl http://localhost:5000/api/profile

# Get logs
curl http://localhost:5000/api/logs
```

## Documentation

- [Full Documentation](docs/README.md) - Complete API reference and examples
- [Setup Guide](docs/SETUP.md) - Quick setup reference
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed file descriptions

## Important Notes

- **For demo purposes only** - No authentication/security
- All requests use a single demo user (ID: 1)
- Server runs on `http://localhost:5000`
- CORS enabled for all origins
- Max upload size: 16MB

## Troubleshooting

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

**Good luck with your hackathon!**