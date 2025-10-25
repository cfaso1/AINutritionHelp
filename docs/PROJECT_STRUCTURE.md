# Project Structure

## 📂 Organized Folder Layout

```
AINutritionHelp/
│
├── run.py                      # 🚀 START HERE - Main entry point
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # Quick start guide
│
├── backend/                    # 🔧 Backend Code
│   ├── __init__.py            # Python package file
│   ├── api_simple.py          # REST API (no authentication)
│   ├── database.py            # SQLite database functions
│   ├── nutrition_reader.py   # OCR nutrition label scanner
│   ├── ai_model.py            # Custom AI model integration
│   ├── nutrition_json.json    # Sample nutrition data format
│   ├── uploads/               # Uploaded images (auto-created)
│   └── nutrition_app.db       # SQLite database (auto-created)
│
├── frontend/                   # 🎨 Frontend Code
│   └── demo.html              # Web interface with drag & drop
│
├── docs/                       # 📚 Documentation
│   ├── README.md              # Full documentation
│   ├── SETUP.md               # Quick setup guide
│   └── PROJECT_STRUCTURE.md   # This file - detailed structure
│
└── venv/                       # Python virtual environment
```

## 🚀 How to Run

```bash
# Simple!
python run.py
```

Then open [frontend/demo.html](../frontend/demo.html) in your browser.

## 📝 File Descriptions

### Root Level
- **run.py** - Main entry point, starts the API server
- **requirements.txt** - All Python dependencies
- **.gitignore** - Files to ignore in git
- **README.md** - Quick start guide

### Backend/
- **api_simple.py** - Flask REST API with all endpoints
- **database.py** - Database functions (CRUD operations)
- **nutrition_reader.py** - OCR scanner using Tesseract
- **ai_model.py** - Your custom AI model integration point
- **nutrition_json.json** - Sample nutrition data format (example structure)
- **__init__.py** - Makes backend a Python package

### Frontend/
- **demo.html** - Complete web interface with:
  - Drag & drop image upload
  - Nutrition scanning
  - AI analysis
  - Daily stats dashboard
  - Nutrition logs

### Docs/
- **README.md** - Complete documentation
- **SETUP.md** - Quick setup reference
- **PROJECT_STRUCTURE.md** - This file - detailed structure info

## 🔄 Data Flow

```
User (frontend/demo.html)
    ↓
Upload Image
    ↓
API (backend/api_simple.py)
    ↓
OCR Scanner (backend/nutrition_reader.py)
    ↓
Structured JSON
    ↓
AI Analysis (backend/ai_model.py) ← Your model here!
    ↓
Database (backend/database.py)
    ↓
Response to User
```

## 🎯 Next Steps

1. **Test**: Open `frontend/demo.html`
2. **Train AI**: Create your nutrition analysis model
3. **Integrate**: Update `backend/ai_model.py`
4. **Customize**: Edit `frontend/demo.html` for branding

---

**Everything is organized and ready for your hackathon!**
