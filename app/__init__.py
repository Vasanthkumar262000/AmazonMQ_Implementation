"""
============================================
FLASK APPLICATION INITIALIZATION
============================================

This file creates and configures the Flask application.
It's the entry point for our web API.

What this file does:
1. Creates the Flask app instance
2. Enables CORS (Cross-Origin Resource Sharing)
3. Loads configuration from environment variables
4. Registers all API routes

Flask is a "micro" web framework - it's lightweight but powerful.
Perfect for building REST APIs quickly.
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# Flask - The web framework that handles HTTP requests
from flask import Flask

# CORS - Allows requests from different domains (Postman, browsers, etc.)
from flask_cors import CORS


def create_app():
    """
    Application Factory Pattern
    ---------------------------
    This function creates and configures the Flask application.
    
    Why use a factory function?
    - Makes testing easier (can create multiple app instances)
    - Allows different configurations for dev/test/prod
    - Cleaner code organization
    
    Returns:
        Flask app: Configured Flask application ready to run
    """
    
    # --------------------------------------------
    # STEP 1: Create Flask Application
    # --------------------------------------------
    # __name__ tells Flask where to look for templates and static files
    # In our case, it's the 'app' package
    app = Flask(__name__)
    
    # --------------------------------------------
    # STEP 2: Enable CORS
    # --------------------------------------------
    # CORS = Cross-Origin Resource Sharing
    # Without this, browsers would block requests from Postman or other origins
    # This allows ANY origin to call our API (fine for demo, restrict in production)
    CORS(app)
    
    # --------------------------------------------
    # STEP 3: Load Configuration
    # --------------------------------------------
    # Import our configuration class
    from app.config import Config
    
    # Apply all configuration values to the app
    # This loads things like RABBITMQ_HOST, RABBITMQ_PORT, etc.
    app.config.from_object(Config)
    
    # --------------------------------------------
    # STEP 4: Register Routes (API Endpoints)
    # --------------------------------------------
    # Import the routes blueprint
    from app.routes import api_blueprint
    
    # Register the blueprint with URL prefix /api
    # All routes in routes.py will be prefixed with /api
    # Example: /orders becomes /api/orders
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # --------------------------------------------
    # STEP 5: Add Root Route
    # --------------------------------------------
    @app.route('/')
    def index():
        """
        Root endpoint - shows welcome message
        Useful for quick health check
        """
        return {
            'message': 'Amazon MQ Demo API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'create_order': 'POST /api/orders',
                'list_orders': 'GET /api/orders',
                'queue_stats': '/api/queue/stats'
            }
        }
    
    # Return the configured app
    return app
