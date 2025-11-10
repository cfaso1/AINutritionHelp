#!/usr/bin/env python3
"""
Run the AI Nutrition Help API server.
Production-ready with environment-based configuration.

Usage:
    python run.py                    # Development mode (default)
    FLASK_ENV=production python run.py  # Production mode
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration
from config.config import active_config as Config

# Validate configuration before starting
try:
    Config.validate()
except ValueError as e:
    print("\n❌ Configuration Error:")
    print(str(e))
    print("\n📝 Please check your .env file and ensure all required variables are set.")
    print("   Copy .env.example to .env and fill in the values.\n")
    sys.exit(1)

# Import and run the API
from backend.api import app

if __name__ == '__main__':
    # Only show banner once (not in reloader child process)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n" + "="*60)
        print("  🍎 AI Nutrition Help API - Production Ready")
        print("="*60)
        print(f"  Environment: {Config.FLASK_ENV}")
        print(f"  Server: http://{Config.HOST}:{Config.PORT}")
        print(f"  Debug Mode: {'ON' if Config.FLASK_DEBUG else 'OFF'}")
        print(f"  Rate Limiting: {'ON' if Config.RATE_LIMIT_ENABLED else 'OFF'}")
        print(f"  CORS Origins: {', '.join(Config.ALLOWED_ORIGINS)}")
        print("="*60 + "\n")

    # Start the Flask application
    app.run(
        debug=Config.FLASK_DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
