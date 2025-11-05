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
    print("Get API key: https://aistudio.google.com/apikey")
    print("Add to .env: GOOGLE_API_KEY=your_key_here\n")
    sys.exit(1)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the API
from backend.api import app

if __name__ == '__main__':
    # Only show banner once (not in reloader child process)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n🍎 AI Nutrition Help API")
        print("=" * 50)
        print("Server: http://localhost:5000")
        print("Frontend: Open frontend/index.html in browser")
        print("Demo Login: demo_user / demo123")
        print("=" * 50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
