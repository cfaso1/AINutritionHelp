#!/usr/bin/env python3
"""
Run the AI Nutrition Help API server.
Usage: python run.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the API
from backend.api_simple import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🍎 AI Nutrition Help API Server")
    print("="*70)
    print("\n✨ Features: OCR Scanner | Health Goals | Food Log | AI Analysis\n")
    print("API Endpoints:")
    print("  Authentication:")
    print("    POST   http://localhost:5000/api/auth/register")
    print("    POST   http://localhost:5000/api/auth/login")
    print("\n  Profile & Goals:")
    print("    GET    http://localhost:5000/api/profile")
    print("    PUT    http://localhost:5000/api/profile")
    print("\n  Nutrition:")
    print("    POST   http://localhost:5000/api/scan")
    print("    POST   http://localhost:5000/api/analyze")
    print("    POST   http://localhost:5000/api/log")
    print("    GET    http://localhost:5000/api/logs")
    print("\n  Weight Tracking:")
    print("    POST   http://localhost:5000/api/weight")
    print("    GET    http://localhost:5000/api/weight/history")
    print("\n" + "="*70)
    print("\n🚀 Open frontend/demo.html in your browser!")
    print("   Demo Account: demo_user / demo123")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
