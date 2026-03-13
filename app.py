from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Initialize Firebase
from config.firebase_config import db

# Register Blueprints (routes)
from routes.navigation import navigation_bp
app.register_blueprint(navigation_bp, url_prefix='/api/navigation')

from routes.users import users_bp
from routes.alerts import alerts_bp

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(alerts_bp, url_prefix='/api/alerts')

# Health check route
@app.route('/')
def index():
    return {"message": "SOSConnect API is running!"}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)