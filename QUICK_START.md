# 🚀 Quick Start Guide

## Launch in 3 Steps

### 1️⃣ Start Backend
```bash
cd /home/charlie/Documents/CS_Projects/AINutritionHelp
python3 run.py
```

**Expected output:**
```
🍎 AI Nutrition Help API Server
API Endpoints:
  POST   http://localhost:5000/api/barcode/scan
  POST   http://localhost:5000/api/barcode/image
  POST   http://localhost:5000/api/agent/evaluate
🚀 Open frontend/demo.html in your browser!
```

### 2️⃣ Open Frontend
```bash
# Open in browser
firefox frontend/index_cyber.html
# or
google-chrome frontend/index_cyber.html
```

### 3️⃣ Scan Products

**Option A: Enter Barcode**
1. Click "LAUNCH SCANNER"
2. Type: `722252601025`
3. Press Enter
4. Click "GET AI ANALYSIS"

**Option B: Quick Test**
1. Click "LAUNCH SCANNER"
2. Click any barcode in the sidebar
3. Click "GET AI ANALYSIS"

## Test Barcodes

| Barcode | Product | Best For Testing |
|---------|---------|------------------|
| `722252601025` | Quest Protein Bar | Fitness analysis (high protein) |
| `012000161551` | Coca-Cola | Health warnings (high sugar) |
| `078000113464` | Gatorade | Sports nutrition |
| `016000275683` | Cheerios | Breakfast/fiber analysis |

## What You'll See

### Product Info
- Name, brand, category
- Price and size
- Full nutrition facts grid

### AI Analysis
- **Overall Score** (0-100)
- **Health Analysis**: Score, pros, cons
- **Fitness Analysis**: Score, best use, recommendations
- **Price Evaluation**: Rating and value assessment

## Troubleshooting

**Backend won't start?**
```bash
pip install -r requirements.txt
```

**"Product not found"?**
- Use one of the test barcodes above
- Real barcode API may not have all products
- System falls back to mock data for test barcodes

**No AI analysis?**
- Analysis will use rule-based fallbacks
- Check `.env` for valid `ANTHROPIC_API_KEY` if you want full AI
- Fallback system still provides useful analysis

## Files Changed

✅ **NEW**: `frontend/index_cyber.html` - Cyberpunk UI
✅ **FIXED**: `nutrition_agent/services/barcode_api.py` - No more fake sample data
✅ **IMPROVED**: All AI agents now have fallback logic

## Documentation

- 📖 [REDESIGN_GUIDE.md](REDESIGN_GUIDE.md) - Full redesign details
- 📋 [TEST_BARCODES.md](TEST_BARCODES.md) - Available test products
- 📘 [README.md](README.md) - Original project documentation

---

**That's it! Start scanning! 📱🤖**
