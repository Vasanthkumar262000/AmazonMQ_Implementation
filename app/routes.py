"""
============================================
API ROUTES
============================================

This module defines all REST API endpoints.

Endpoints:
- POST /api/orders       - Create a new order
- GET  /api/orders       - List recent orders (from memory)
- POST /api/orders/batch - Create multiple test orders
- GET  /api/health       - Health check
- GET  /api/queue/stats  - Queue statistics

These endpoints are called from Postman or any HTTP client.
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# Flask components
from flask import Blueprint, request, jsonify

# datetime for timestamps
from datetime import datetime

# Import our producer
from app.producer import OrderProducer, send_order

# Import RabbitMQ client for queue stats
from app.rabbitmq_client import get_rabbitmq_client

# Import config
from app.config import Config


# --------------------------------------------
# CREATE BLUEPRINT
# --------------------------------------------
# A Blueprint is a way to organize routes
# All routes here will be prefixed with /api
api_blueprint = Blueprint('api', __name__)


# In-memory storage for demo (shows orders sent in this session)
recent_orders = []


# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@api_blueprint.route('/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---------------------
    GET /api/health
    
    Checks if the API and RabbitMQ connection are working.
    
    Returns:
        JSON with status of each component
    
    Example Response:
    {
        "status": "healthy",
        "api": "running",
        "rabbitmq": "connected",
        "queue": "orders",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    try:
        # Check RabbitMQ connection
        client = get_rabbitmq_client()
        stats = client.get_queue_stats()
        rabbitmq_status = "connected"
        queue_messages = stats['message_count']
    except Exception as e:
        rabbitmq_status = f"error: {str(e)}"
        queue_messages = -1
    
    return jsonify({
        'status': 'healthy' if rabbitmq_status == 'connected' else 'degraded',
        'api': 'running',
        'rabbitmq': rabbitmq_status,
        'queue': Config.QUEUE_NAME,
        'messages_in_queue': queue_messages,
        'timestamp': datetime.utcnow().isoformat()
    })


# ============================================
# CREATE ORDER ENDPOINT
# ============================================

@api_blueprint.route('/orders', methods=['POST'])
def create_order():
    """
    Create Order Endpoint
    ---------------------
    POST /api/orders
    
    Creates a new order and publishes it to the RabbitMQ queue.
    
    Request Body (JSON):
    {
        "customer_name": "John Doe",
        "email": "john@example.com",
        "items": [
            {"product": "iPhone 15", "quantity": 1, "price": 999.00}
        ],
        "shipping_address": "123 Main St, New York, NY 10001",
        "order_type": "standard"  // optional: standard, express, prime
    }
    
    Returns:
        JSON with order confirmation
    
    Example Response:
    {
        "success": true,
        "order_id": "ORD-20240115-a1b2c3d4",
        "message_id": "uuid-here",
        "total": 999.00,
        "status": "pending",
        "message": "Order has been queued for processing"
    }
    """
    try:
        # ----------------------------------------
        # STEP 1: Get JSON data from request
        # ----------------------------------------
        # request.get_json() parses the JSON body
        data = request.get_json()
        
        # Check if we got valid JSON
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'hint': 'Make sure Content-Type is application/json'
            }), 400
        
        # ----------------------------------------
        # STEP 2: Create order via producer
        # ----------------------------------------
        producer = OrderProducer()
        result = producer.create_order(data)
        
        # ----------------------------------------
        # STEP 3: Store in memory (for listing)
        # ----------------------------------------
        recent_orders.append({
            'order_id': result['order_id'],
            'total': result['total'],
            'status': 'queued',
            'created_at': datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 orders in memory
        if len(recent_orders) > 100:
            recent_orders.pop(0)
        
        # ----------------------------------------
        # STEP 4: Return success response
        # ----------------------------------------
        return jsonify(result), 201  # 201 = Created
        
    except ValueError as e:
        # Validation error (missing fields, etc.)
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'validation_error'
        }), 400
        
    except Exception as e:
        # Unexpected error
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'internal_error'
        }), 500


# ============================================
# LIST ORDERS ENDPOINT
# ============================================

@api_blueprint.route('/orders', methods=['GET'])
def list_orders():
    """
    List Orders Endpoint
    --------------------
    GET /api/orders
    
    Returns list of orders created in this session.
    
    Note: This shows orders from memory, not from the queue.
    To see queue contents, use QueueExplorer or /api/queue/stats
    
    Returns:
        JSON with list of recent orders
    """
    return jsonify({
        'count': len(recent_orders),
        'orders': recent_orders,
        'note': 'These are orders from this session. Use QueueExplorer to see queue contents.'
    })


# ============================================
# CREATE BATCH ORDERS ENDPOINT
# ============================================

@api_blueprint.route('/orders/batch', methods=['POST'])
def create_batch_orders():
    """
    Create Batch Orders Endpoint
    ----------------------------
    POST /api/orders/batch
    
    Creates multiple test orders for demo purposes.
    Useful for populating the queue quickly.
    
    Request Body (JSON):
    {
        "count": 10  // Number of orders to create (max 50)
    }
    
    Returns:
        JSON with list of created orders
    """
    try:
        data = request.get_json() or {}
        count = min(int(data.get('count', 5)), 50)  # Max 50 orders
        
        producer = OrderProducer()
        results = producer.create_test_orders(count)
        
        # Store in memory
        for result in results:
            recent_orders.append({
                'order_id': result['order_id'],
                'total': result['total'],
                'status': 'queued',
                'created_at': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'success': True,
            'count': len(results),
            'orders': results,
            'message': f'Created {len(results)} test orders'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# QUEUE STATISTICS ENDPOINT
# ============================================

@api_blueprint.route('/queue/stats', methods=['GET'])
def queue_stats():
    """
    Queue Statistics Endpoint
    -------------------------
    GET /api/queue/stats
    
    Returns statistics about the RabbitMQ queue.
    
    Returns:
        JSON with queue information
    
    Example Response:
    {
        "queue_name": "orders",
        "message_count": 42,
        "consumer_count": 1,
        "connection": {
            "host": "xxx.mq.us-east-1.amazonaws.com",
            "port": 5671,
            "ssl": true
        }
    }
    """
    try:
        client = get_rabbitmq_client()
        stats = client.get_queue_stats()
        
        return jsonify({
            **stats,
            'connection': Config.get_connection_info()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'queue_name': Config.QUEUE_NAME,
            'connection': Config.get_connection_info()
        }), 500


# ============================================
# ERROR HANDLERS
# ============================================

@api_blueprint.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404


@api_blueprint.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500
