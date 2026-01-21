"""
Vercel Serverless Function Entry Point
Wraps api_minimal.py FastAPI app for Vercel deployment
"""

import sys
import os

# Add parent directory to path to import api_minimal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_minimal import app

# Vercel expects a handler function
handler = app
