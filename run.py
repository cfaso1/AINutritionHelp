#!/usr/bin/env python3
"""
Run the AI Nutrition Help API server.
Usage: python run.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the API
from backend.api_simple import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🍎 AI Nutrition Help API Server")
    print("="*70)
    print("\n✨ Features: Barcode Scanner | Multi-Agent AI | Health Goals\n")
    print("API Endpoints:")
    print("  Authentication:")
    print("    POST   http://localhost:5000/api/auth/register")
    print("    POST   http://localhost:5000/api/auth/login")
    print("\n  Profile & Goals:")
    print("    GET    http://localhost:5000/api/profile")
    print("    PUT    http://localhost:5000/api/profile")
    print("\n  Barcode Scanning & AI:")
    print("    POST   http://localhost:5000/api/barcode/scan")
    print("    POST   http://localhost:5000/api/barcode/image")
    print("    POST   http://localhost:5000/api/agent/evaluate")
    print("\n  Weight Tracking:")
    print("    POST   http://localhost:5000/api/weight")
    print("    GET    http://localhost:5000/api/weight/history")
    print("\n" + "="*70)
    print("\n🚀 Open frontend/demo.html in your browser!")
    print("   Demo Account: demo_user / demo123")
    print("\n💡 TIP: Make sure to install dependencies:")
    print("   pip install -r requirements.txt")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
