#!/usr/bin/env python3
"""
Run the AI Nutrition Help API server.
Usage: python run.py
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for required Google API key
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_KEY:
    print("\n❌ ERROR: Missing GOOGLE_API_KEY in .env file")
    print("\n📝 To fix this:")
    print("   1. Get an API key from: https://aistudio.google.com/apikey")
    print("   2. Add it to your .env file: GOOGLE_API_KEY=your_key_here")
    print("   3. Restart the server\n")
    sys.exit(1)

print("✅ Google API Key loaded")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the API
from backend.api_simple import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🍎 AI Nutrition Help API Server")
    print("="*70)
    print("\n✨ Features: Nutrition Scanner | AI Chat | Multi-Agent Analysis\n")
    print("API Endpoints:")
    print("  Authentication:")
    print("    POST   http://localhost:5000/api/auth/register")
    print("    POST   http://localhost:5000/api/auth/login")
    print("\n  Profile & Goals:")
    print("    GET    http://localhost:5000/api/profile")
    print("    PUT    http://localhost:5000/api/profile")
    print("    POST   http://localhost:5000/api/profile/setup")
    print("\n  Nutrition Scanning & AI:")
    print("    POST   http://localhost:5000/api/nutrition/ocr")
    print("    POST   http://localhost:5000/api/nutrition/manual")
    print("    POST   http://localhost:5000/api/nutrition/clarify")
    print("    POST   http://localhost:5000/api/agent/evaluate")
    print("    POST   http://localhost:5000/api/agent/chat")
    print("\n  Weight Tracking:")
    print("    POST   http://localhost:5000/api/weight")
    print("    GET    http://localhost:5000/api/weight/history")
    print("\n" + "="*70)
    print("\n🚀 Open frontend/index.html in your browser!")
    print("   Demo Account: demo_user / demo123")
    print("\n💡 Powered by Google Gemini 2.0-flash")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
