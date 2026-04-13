"""
============================================
CONFIGURATION MANAGEMENT
============================================

This file handles all application configuration.
It reads values from environment variables (set in .env file).

Why use environment variables?
- Security: Passwords and secrets aren't in the code
- Flexibility: Different values for dev/test/prod
- Best Practice: 12-factor app methodology

How it works:
1. python-dotenv loads variables from .env file
2. os.getenv() reads each variable
3. Config class provides defaults if variable not set
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# os - Operating system interface, used to read environment variables
import os

# load_dotenv - Reads .env file and sets environment variables
from dotenv import load_dotenv

# --------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------
# This reads the .env file in the project root
# and sets all variables as environment variables
load_dotenv()


class Config:
    """
    Configuration Class
    -------------------
    Stores all configuration values for the application.
    
    Each value is read from environment variables with a default fallback.
    
    Usage:
        from app.config import Config
        host = Config.RABBITMQ_HOST
    """
    
    # ============================================
    # RABBITMQ / AMAZON MQ SETTINGS
    # ============================================
    
    # RABBITMQ_HOST
    # The hostname of your Amazon MQ broker
    # Format: b-xxxx.mq.us-east-1.amazonaws.com
    # Default: localhost (for local development)
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    
    # RABBITMQ_PORT
    # Port number for RabbitMQ connection
    # Amazon MQ uses 5671 for SSL connections
    # Local RabbitMQ typically uses 5672 (non-SSL)
    # int() converts the string to an integer
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
    
    # RABBITMQ_USERNAME
    # Username for authentication
    # This is set when creating the Amazon MQ broker
    RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME', 'guest')
    
    # RABBITMQ_PASSWORD
    # Password for authentication
    # NEVER hardcode this in production code!
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    
    # RABBITMQ_VHOST
    # Virtual host in RabbitMQ
    # Virtual hosts provide logical separation of queues
    # Default "/" is the root virtual host
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    
    # ============================================
    # QUEUE SETTINGS
    # ============================================
    
    # QUEUE_NAME
    # Name of the main queue for order messages
    # This is where new orders are published
    QUEUE_NAME = os.getenv('QUEUE_NAME', 'orders')
    
    # DLQ_NAME
    # Dead Letter Queue name
    # Failed messages are sent here for investigation
    DLQ_NAME = os.getenv('DLQ_NAME', 'orders.dlq')
    
    # ============================================
    # FLASK API SETTINGS
    # ============================================
    
    # API_PORT
    # Port number for the Flask API server
    # Default 5000 is Flask's standard development port
    API_PORT = int(os.getenv('API_PORT', '5000'))
    
    # FLASK_DEBUG
    # Enable debug mode for development
    # Set to False in production!
    # Debug mode provides better error messages and auto-reload
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    @classmethod
    def is_amazon_mq(cls):
        """
        Check if we're connecting to Amazon MQ
        
        Amazon MQ uses port 5671 with SSL
        Local RabbitMQ uses port 5672 without SSL
        
        Returns:
            bool: True if connecting to Amazon MQ
        """
        return cls.RABBITMQ_PORT == 5671
    
    @classmethod
    def get_connection_info(cls):
        """
        Get a safe representation of connection info (no password)
        
        Useful for logging and debugging
        
        Returns:
            dict: Connection details without sensitive info
        """
        return {
            'host': cls.RABBITMQ_HOST,
            'port': cls.RABBITMQ_PORT,
            'username': cls.RABBITMQ_USERNAME,
            'vhost': cls.RABBITMQ_VHOST,
            'ssl': cls.is_amazon_mq(),
            'queue': cls.QUEUE_NAME
        }
    
    @classmethod
    def print_config(cls):
        """
        Print configuration (for debugging)
        
        Masks the password for security
        """
        print("\n" + "="*50)
        print("CONFIGURATION")
        print("="*50)
        print(f"RabbitMQ Host: {cls.RABBITMQ_HOST}")
        print(f"RabbitMQ Port: {cls.RABBITMQ_PORT}")
        print(f"RabbitMQ User: {cls.RABBITMQ_USERNAME}")
        print(f"RabbitMQ Pass: {'*' * len(cls.RABBITMQ_PASSWORD)}")
        print(f"Virtual Host:  {cls.RABBITMQ_VHOST}")
        print(f"Queue Name:    {cls.QUEUE_NAME}")
        print(f"SSL Enabled:   {cls.is_amazon_mq()}")
        print("="*50 + "\n")
