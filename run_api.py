#!/usr/bin/env python3
"""
============================================
RUN API SERVER
============================================

This is the main entry point for the Flask API server.

Usage:
    python run_api.py

What it does:
1. Loads environment variables from .env
2. Creates the Flask application
3. Tests RabbitMQ connection
4. Starts the web server

The API will be available at:
    http://localhost:5000

Endpoints:
    GET  /api/health       - Health check
    POST /api/orders       - Create new order
    GET  /api/orders       - List recent orders
    POST /api/orders/batch - Create test orders
    GET  /api/queue/stats  - Queue statistics
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# Load environment variables FIRST
# This must happen before importing app modules
from dotenv import load_dotenv
load_dotenv()

# Now import our app
from app import create_app
from app.config import Config


def main():
    """
    Main function to start the API server
    """
    # Print banner
    print("\n" + "="*60)
    print("🚀 AMAZON MQ DEMO API")
    print("="*60)
    
    # Print configuration (password masked)
    Config.print_config()
    
    # Create Flask app
    app = create_app()
    
    # Test RabbitMQ connection
    print("Testing RabbitMQ connection...")
    try:
        from app.rabbitmq_client import get_rabbitmq_client
        client = get_rabbitmq_client()
        stats = client.get_queue_stats()
        print(f"✅ RabbitMQ connected! Queue has {stats['message_count']} messages")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to RabbitMQ: {e}")
        print("   The API will start, but order creation may fail.")
    
    # Print startup info
    print("\n" + "="*60)
    print("🌐 STARTING WEB SERVER")
    print("="*60)
    print(f"   URL:  http://localhost:{Config.API_PORT}")
    print(f"   Mode: {'Development' if Config.FLASK_DEBUG else 'Production'}")
    print("="*60)
    print("\n📋 AVAILABLE ENDPOINTS:")
    print("   GET  http://localhost:5000/              - Welcome")
    print("   GET  http://localhost:5000/api/health    - Health check")
    print("   POST http://localhost:5000/api/orders    - Create order")
    print("   GET  http://localhost:5000/api/orders    - List orders")
    print("   POST http://localhost:5000/api/orders/batch - Create test orders")
    print("   GET  http://localhost:5000/api/queue/stats  - Queue stats")
    print("\n" + "="*60)
    print("   Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run the Flask development server
    # In production, use gunicorn or uwsgi instead
    app.run(
        host='0.0.0.0',           # Listen on all interfaces
        port=Config.API_PORT,     # Port from config (default 5000)
        debug=Config.FLASK_DEBUG  # Debug mode from config
    )


# --------------------------------------------
# ENTRY POINT
# --------------------------------------------
# This runs when you execute: python run_api.py

if __name__ == '__main__':
    main()
