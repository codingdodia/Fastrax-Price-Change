import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

# Set environment variable to indicate we're running on Vercel
os.environ['VERCEL'] = '1'

# This is the entry point for Vercel
app = app