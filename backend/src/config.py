# config.py
from flask import Flask
from flask_cors import CORS
import os


app = Flask(__name__)

# Configure CORS for production and development
if os.environ.get('VERCEL'):
    # Production configuration
    CORS(app, origins=['*'])  # You can restrict this to your domain
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
else:
    # Development configuration
    CORS(app)
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True

