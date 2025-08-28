#!/usr/bin/env python3
"""
Sorachain Provisioning Dashboard Application Factory
"""
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS to allow all origins
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"]
        }
    })
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///provisioning_dashboard.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # JWT Configuration for development
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # No expiration for development
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = False  # No expiration for development
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Add JWT error handlers for debugging
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"❌ JWT Invalid token: {error}")
        return jsonify({"error": "Invalid token"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"❌ JWT Missing token: {error}")
        return jsonify({"error": "Missing authorization header"}), 401
    
    # Add a test endpoint to verify JWT is working
    @app.route('/api/v1/test-jwt', methods=['GET'])
    @jwt_required()
    def test_jwt():
        current_user_email = get_jwt_identity()
        print(f"✅ JWT test successful - user: {current_user_email}")
        return jsonify({"message": "JWT is working", "user": current_user_email })
    
    # Add before_request handler to log all requests
    @app.before_request
    def log_request_info():
        print(f"🌐 Request: {request.method} {request.path}")
        if request.method in ['POST', 'PUT', 'PATCH']:
            print(f"🌐 Body: {request.get_data(as_text=True)}")
    
    # Import and register blueprints
    from .views import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    return app

def init_database(app):
    """Initialize database tables and default data"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
            
            # Initialize default data if needed
            from .models import init_default_data
            init_default_data()
            print("Database initialization completed")
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Don't fail the app startup, just log the error

