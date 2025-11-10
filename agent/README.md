# Nutrition AI Agent - Production v2.0

A comprehensive, production-ready AI companion for personalized nutrition evaluation and recommendations.

## 🎯 Overview

The Nutrition AI Agent is a modular, scalable system that combines AI-powered nutrition analysis and conversational companion behavior to help users make informed food choices aligned with their health and fitness goals.

## 🏗️ Architecture

```
agent/
├── main_agent.py           # Main orchestrator - coordinates all components
├── health_evaluator.py     # Health & wellness analysis
├── fitness_evaluator.py    # Fitness & workout recommendations
├── price_evaluator.py      # Pricing & value analysis
├── models.py               # Data models (Product, UserProfile)
├── service.py              # Backend integration layer
├── utils/
│   ├── data_parser.py      # Nutrition data parsing & normalization
│   └── response_formatter.py # Response formatting utilities
└── __init__.py             # Package exports
```

## ✨ Features

### Core Capabilities

1. **Health Evaluation** - Analyze nutritional alignment with health goals
2. **Fitness Evaluation** - Assess products for workout and activity needs
3. **Price Evaluation** - Determine value for money and suggest alternatives
4. **Conversational AI** - Friendly, personalized companion messages

### AI Model

- **Model**: Google Gemini 2.0-flash-exp
- **Benefits**: Fast, accurate, conversational responses
- **Capabilities**: Natural language understanding, personalized recommendations

## 📦 Installation

### Requirements

```bash
Python 3.12+
Google API Key (for Gemini)
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or with virtual environment:

```bash
./venv/bin/pip install -r requirements.txt
```

### Configuration

Add to root `.env` (project root directory):

```env
GOOGLE_API_KEY=your_google_api_key_here
```

## 🚀 Usage

### Quick Start

```python
import asyncio
from agent import get_agent
from agent.models import UserProfile, Product

async def main():
    # Initialize agent
    agent = get_agent()

    # Create product from nutrition data
    product = Product(
        name="Greek Yogurt",
        brand="Chobani",
        category="Dairy",
        price=1.99,
        nutrition={
            "calories": 100,
            "protein": 17,
            "carbs_total": 6,
            "sugar_total": 4,
            "fat_total": 0,
            "sodium": 60
        }
    )

    # Create user profile
    profile = UserProfile(
        health_goals="low sugar, high protein",
        fitness_goals="muscle building",
        daily_protein_target_g=150
    )

    # Evaluate product
    evaluation = await agent.evaluate_product(product, profile)

    # Print results
    print(f"Score: {evaluation['overall']['score']}/100")
    print(f"Message: {evaluation['companion_message']}")

asyncio.run(main())
```

### Test via API

The agent is integrated into the Flask backend. Test it by:
1. Starting the backend: `python run.py`
2. Using the frontend or making API calls to `/api/agent/evaluate` or `/api/agent/chat`

### Backend Integration

```python
from agent import get_nutrition_agent_service, run_async

# Get service
service = get_nutrition_agent_service()

# Use in Flask routes with nutrition data from OCR or manual entry
evaluation = run_async(service.evaluate_product(product_data, user_profile_data))
```

## 📚 API Reference

### NutritionAgent

Main agent class coordinating all evaluations.

#### Methods

**`evaluate_product(product: Product, user_profile: UserProfile) -> Dict`**
- Comprehensive evaluation with all three evaluators
- Returns health, fitness, price analysis + companion message

**`chat(message: str, context: Optional[Dict]) -> str`**
- Interactive chat with AI companion
- Provides personalized nutrition advice

### Evaluators

#### HealthEvaluator

Analyzes products for health and wellness alignment.

**Output:**
- `score`: 0-100 health alignment score
- `summary`: Friendly 2-3 sentence summary
- `pros`: List of nutritional positives (top 3)
- `cons`: List of nutritional concerns (top 3)

#### FitnessEvaluator

Evaluates products for fitness goals and activity needs.

**Output:**
- `score`: 0-100 fitness alignment score
- `summary`: Friendly 2-3 sentence summary
- `best_for`: Best timing (e.g., "pre-workout", "post-workout")
- `recommendation`: Specific actionable recommendation

#### PriceEvaluator

Analyzes product pricing and value for money.

**Output:**
- `rating`: "Excellent Deal", "Good Price", "Fair Price", or "Expensive"
- `is_good_deal`: Boolean value indicator
- `unit_price`: Calculated unit price
- `category_average`: Category average for comparison
- `summary`: Friendly price analysis
- `comparison_percent`: Percentage above/below average

## 🔧 Utilities

### Data Parser

```python
from agent.utils.data_parser import parse_nutrition_data, calculate_macros

# Parse nutrition data
nutrition = parse_nutrition_data(raw_data)

# Calculate macro percentages
macros = calculate_macros(protein=21, carbs=22, fat=8)
# Returns: {protein_percent: 35.0, carb_percent: 37.0, fat_percent: 28.0}
```

### Response Formatter

```python
from agent.utils.response_formatter import format_evaluation_response

# Format complete evaluation
response = format_evaluation_response(
    product, health_analysis, fitness_analysis,
    price_analysis, companion_message
)
```

## 🔌 Backend Integration

The agent integrates seamlessly with the existing Flask backend:

### Endpoints

- **`/api/agent/evaluate`** - Comprehensive product evaluation
- **`/api/agent/chat`** - Chat with AI companion
- **`/api/nutrition/ocr`** - Upload nutrition label image
- **`/api/nutrition/manual`** - Manual nutrition data entry

### Integration Layer

`service.py` provides a backward-compatible wrapper around the main agent for Flask integration.

## 📊 Example Output

```json
{
  "product": {
    "name": "Quest Protein Bar - Chocolate Chip Cookie Dough",
    "brand": "Quest Nutrition",
    "price": 2.49
  },
  "health_analysis": {
    "score": 85,
    "summary": "Excellent high-protein, low-sugar option...",
    "pros": ["21g protein", "Low sugar (1g)", "High fiber (14g)"],
    "cons": ["Processed ingredients", "Moderate sodium"]
  },
  "fitness_analysis": {
    "score": 85,
    "summary": "Perfect for muscle recovery and growth...",
    "best_for": "post-workout recovery",
    "recommendation": "Consume within 30 minutes post-workout"
  },
  "price_analysis": {
    "rating": "Expensive",
    "is_good_deal": false,
    "summary": "Premium pricing for premium protein..."
  },
  "overall": {
    "score": 85.0,
    "recommendation": "Highly Recommended",
    "recommendation_emoji": "✅"
  },
  "companion_message": "Hey there! I just looked at the Quest Chocolate Chip Cookie Dough Protein Bar you scanned..."
}
```

## 🎨 Customization

### Adding New Evaluators

Create a new evaluator class in a separate file:

```python
# agent/environmental_evaluator.py
from agent.models import Product, UserProfile
from typing import Dict

class EnvironmentalEvaluator:
    async def evaluate(self, product: Product, user_profile: UserProfile) -> Dict:
        # Your evaluation logic
        return {
            "score": 85,
            "summary": "...",
            "carbon_footprint": "low",
            "packaging": "recyclable"
        }
```

Add to `main_agent.py`:

```python
from agent.environmental_evaluator import EnvironmentalEvaluator

class NutritionAgent:
    def __init__(self):
        # ... existing code ...
        self.environmental_evaluator = EnvironmentalEvaluator()
```

## 📝 Code Organization

### Clean Architecture Principles

1. **Separation of Concerns** - Each evaluator handles one responsibility
2. **Dependency Injection** - Components receive dependencies
3. **Single Responsibility** - Each module has one clear purpose
4. **DRY (Don't Repeat Yourself)** - Utilities for common operations
5. **Type Safety** - Pydantic models for data validation

### Naming Conventions

- **Classes**: PascalCase (e.g., `NutritionAgent`, `HealthEvaluator`)
- **Functions**: snake_case (e.g., `evaluate_product`, `chat`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `CATEGORY_BENCHMARKS`)
- **Private methods**: `_leading_underscore` (e.g., `_parse_response`)

## 🚨 Error Handling

The agent includes comprehensive error handling:

- **Fallback Analyses** - Basic rule-based evaluations when AI fails
- **Graceful Degradation** - Continues with partial data if evaluations fail
- **User-Friendly Messages** - Clear error messages for users
- **Logging** - Prints errors for debugging while maintaining UX

## 🔒 Production Readiness

### Features

- ✅ Modular, scalable architecture
- ✅ Comprehensive error handling
- ✅ Type-safe with Pydantic models
- ✅ Async/await for performance
- ✅ Singleton pattern for efficiency
- ✅ Clean code with documentation
- ✅ Backward compatible with existing API
- ✅ Production-tested and deployed

### Performance

- **Fast**: Async operations, parallel evaluations
- **Efficient**: Singleton pattern, connection pooling
- **Scalable**: Modular design, easy to extend

## 📄 License

Part of the AI Nutrition Help project.

## 🙏 Credits

Built with:
- Google Gemini AI (genai SDK)
- Pydantic for data validation
- aiohttp for async HTTP requests
- Flask for web framework integration

---

**Version**: 2.0.0 (Production Ready)
**Last Updated**: October 2025
