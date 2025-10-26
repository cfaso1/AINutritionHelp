# Nutrition AI Companion - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites

- Python 3.12+
- Google API Key (for Gemini AI)
- Optional: Barcode Lookup API Key

### Step 1: Install Dependencies

```bash
pip install google-genai pydantic aiohttp python-dotenv
```

Or use the virtual environment:

```bash
./venv/bin/pip install google-genai pydantic aiohttp python-dotenv
```

### Step 2: Configure API Keys

Create or update `agent/.env`:

```env
GOOGLE_API_KEY=your_google_api_key_here
BARCODE_LOOKUP_API_KEY=your_barcode_api_key_here  # Optional
```

**Get a Google API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `.env`

### Step 3: Run the Demo

```bash
./venv/bin/python agent/demo.py
```

You should see:
- 3 product evaluations
- Personalized AI companion messages
- Health, fitness, and price scores
- Conversational recommendations

### Step 4: Start the Backend Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Step 5: Test the API

**Scan a barcode:**

```bash
curl -X POST http://localhost:5000/api/barcode/scan \
  -H "Content-Type: application/json" \
  -d '{"barcode": "722252601025"}'
```

**Evaluate a product:**

```bash
curl -X POST http://localhost:5000/api/agent/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "product": {
      "barcode": "722252601025",
      "name": "Quest Protein Bar",
      "brand": "Quest",
      "category": "health_food",
      "price": 2.49,
      "nutrition": {
        "calories": 200,
        "protein": 21,
        "carbohydrates": 22,
        "sugar": 1,
        "fat": 8,
        "fiber": 14
      }
    }
  }'
```

## 📱 Test Barcodes

Use these for testing:

- `722252601025` - Quest Protein Bar (high protein, recommended)
- `012000161551` - Coca-Cola (high sugar, not recommended)
- `016000275683` - Cheerios (moderate, acceptable with caution)
- `078000113464` - Gatorade (sports drink)
- `028400047685` - Cheez-It (snack)

## 💻 Code Examples

### Basic Usage

```python
import asyncio
from agent import get_companion
from agent.models import UserProfile

async def main():
    # Initialize companion
    companion = get_companion()

    # Scan a product
    product = await companion.scan_barcode("722252601025")

    # Create user profile
    profile = UserProfile(
        health_goals="low sugar, high protein",
        fitness_goals="muscle building",
        daily_protein_target_g=150
    )

    # Evaluate product
    evaluation = await companion.evaluate_product(product, profile)

    # Print results
    print(f"Overall Score: {evaluation['overall']['score']}/100")
    print(f"\nCompanion Message:\n{evaluation['companion_message']}")

asyncio.run(main())
```

### Flask Integration

```python
from flask import Flask, request, jsonify
from agent import get_nutrition_agent_service, run_async

app = Flask(__name__)
service = get_nutrition_agent_service()

@app.route('/api/scan', methods=['POST'])
def scan():
    barcode = request.json['barcode']
    product = run_async(service.scan_barcode(barcode))
    return jsonify(product)

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    product_data = request.json['product']
    user_profile = request.json['profile']
    evaluation = run_async(service.evaluate_product(product_data, user_profile))
    return jsonify(evaluation)
```

## 🎯 API Endpoints

### Backend API (runs on port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/barcode/scan` | POST | Scan a barcode |
| `/api/barcode/image` | POST | Upload barcode image |
| `/api/agent/evaluate` | POST | Evaluate a product |
| `/api/profile` | GET/PUT | User profile |
| `/api/weight` | POST | Log weight |
| `/api/weight/history` | GET | Get weight history |

## 🔧 Troubleshooting

### "Module not found" errors

```bash
# Make sure you're using the virtual environment
./venv/bin/python agent/demo.py

# Or install packages globally
pip install google-genai pydantic aiohttp python-dotenv
```

### "API key not found" errors

```bash
# Check your .env file
cat agent/.env

# Should contain:
GOOGLE_API_KEY=your_key_here
```

### Rate limit errors

The free tier of Google Gemini has rate limits (10 requests/minute). If you hit the limit:

1. Wait 60 seconds
2. Upgrade to paid tier for higher limits
3. Implement rate limiting in your code

### No product found

Make sure you're using one of the test barcodes listed above. The barcode lookup API has limited coverage, so we use mock data for testing.

## 📚 Next Steps

1. **Read the full documentation:** [agent/README.md](agent/README.md)
2. **Review the migration summary:** [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)
3. **Explore the code:** Start with [agent/nutrition_companion.py](agent/nutrition_companion.py)
4. **Customize evaluators:** Modify [agent/evaluators.py](agent/evaluators.py)
5. **Add features:** The architecture is modular and easy to extend

## 🆘 Need Help?

Check these resources:

- **Full README:** [agent/README.md](agent/README.md)
- **Migration Guide:** [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)
- **Demo Script:** [agent/demo.py](agent/demo.py)
- **Google Gemini Docs:** [ai.google.dev](https://ai.google.dev/gemini-api/docs)

## ✅ Verify Installation

Run this simple test:

```python
from agent import get_companion
import asyncio

async def test():
    companion = get_companion()
    product = await companion.scan_barcode("722252601025")
    print(f"✅ Success! Found: {product.name}")

asyncio.run(test())
```

If you see "Success! Found: Quest Protein Bar", you're all set! 🎉

---

**Happy coding!** 🚀
