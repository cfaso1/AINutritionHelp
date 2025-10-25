# Quick Setup Guide

## ✅ What's Ready

Your hackathon nutrition app is **ready to demo** with:
- ✅ REST API (no authentication needed)
- ✅ Beautiful web interface
- ✅ OCR nutrition label scanner
- ✅ SQLite database
- ✅ Custom AI model integration (placeholder ready)
- ✅ All unnecessary files removed

## 🚀 Start Demo in 30 Seconds

```bash
# 1. Start API server
python run.py

# 2. Open frontend/demo.html in your browser
# That's it!
```

## 📂 Your Clean Project Structure

```
run.py                      → START HERE - Main entry point
requirements.txt            → Python dependencies
.gitignore                  → Git ignore rules
README.md                   → Project overview

backend/
  ├── api_simple.py         → REST API (simplified, no auth)
  ├── database.py           → SQLite database functions
  ├── nutrition_reader.py   → OCR scanner
  ├── ai_model.py           → Your custom AI model goes here
  └── nutrition_json.json   → Sample nutrition data format

frontend/
  └── demo.html             → Web interface (drag & drop upload)

docs/
  ├── README.md             → Full documentation
  ├── SETUP.md              → This file - quick setup
  └── PROJECT_STRUCTURE.md  → Detailed structure info
```

## 🤖 Add Your AI Model

Edit `backend/ai_model.py` and replace the `analyze()` method:

```python
def analyze(self, nutrition_data, user_profile):
    # Load your model
    # model = load_model('your_model.pkl')
    
    # Make prediction
    # analysis = model.predict(nutrition_data, user_profile)
    
    return analysis
```

The API automatically uses your model when available!

## 📝 Key Changes Made

### Removed:
- ❌ Authentication system (no login needed!)
- ❌ Session management
- ❌ Password hashing
- ❌ User registration endpoints
- ❌ Third-party AI API code (Claude/OpenAI)
- ❌ Complex security features

### Simplified:
- ✅ Single demo user (ID: 1) for all requests
- ✅ Direct API calls - no authentication required
- ✅ Clean AI model integration point
- ✅ Straightforward frontend examples

## 🔗 API Endpoints (All Open)

No auth required for any endpoint:

- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `POST /api/scan` - Upload & scan label
- `POST /api/analyze` - Get AI analysis
- `POST /api/log` - Save nutrition log
- `GET /api/logs` - View logs
- `POST /api/weight` - Log weight
- `GET /api/weight/history` - View weight history

## 💡 Quick Test

```bash
# Test API
curl http://localhost:5000/api/health

# Get profile
curl http://localhost:5000/api/profile

# View logs
curl http://localhost:5000/api/logs
```

## 🎯 Next Steps

1. **Demo**: Open `frontend/demo.html` and upload a nutrition label
2. **Train AI**: Create your nutrition analysis model
3. **Integrate**: Update `backend/ai_model.py` with your model
4. **Customize**: Edit `frontend/demo.html` for your branding

## ⚠️ Important

- This is for **demo/hackathon use only**
- No security - don't use in production
- All requests use a single demo user
- Perfect for presentations and prototypes!

---

**Your API is running on http://localhost:5000**

**Open frontend/demo.html to start testing!**
