"""
============================================
ORDER PRODUCER
============================================

This module handles creating and publishing order messages.

In a real e-commerce system, this would be called when:
- A customer places an order on the website
- An order is received via API
- An order needs to be reprocessed

The producer:
1. Validates the order data
2. Generates unique order ID
3. Adds metadata
4. Publishes to RabbitMQ queue
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# uuid - Generate unique identifiers
import uuid

# datetime - Timestamps
from datetime import datetime

# typing - Type hints for better code documentation
from typing import Dict, List, Optional

# Import RabbitMQ client
from app.rabbitmq_client import get_rabbitmq_client


class OrderProducer:
    """
    Order Producer Class
    --------------------
    Handles creating and publishing order messages to the queue.
    
    This class:
    - Validates order data
    - Generates order IDs
    - Formats messages for the queue
    - Publishes to RabbitMQ
    """
    
    def __init__(self):
        """
        Initialize the Order Producer
        
        Gets the shared RabbitMQ client instance.
        """
        self.rabbitmq = get_rabbitmq_client()
    
    def create_order(self, order_data: Dict) -> Dict:
        """
        Create and publish a new order
        
        This is the main method for processing new orders.
        
        Args:
            order_data: Dictionary containing order information
                Required fields:
                    - customer_name: Customer's full name
                    - email: Customer's email address
                    - items: List of order items
                    - shipping_address: Delivery address
                
                Optional fields:
                    - order_type: 'standard', 'express', 'prime'
                    - notes: Special instructions
        
        Returns:
            dict: Order confirmation with order_id and message_id
        
        Example:
            producer = OrderProducer()
            result = producer.create_order({
                'customer_name': 'John Doe',
                'email': 'john@example.com',
                'items': [{'product': 'iPhone', 'quantity': 1, 'price': 999}],
                'shipping_address': '123 Main St'
            })
        """
        # ----------------------------------------
        # STEP 1: Validate Required Fields
        # ----------------------------------------
        required_fields = ['customer_name', 'email', 'items', 'shipping_address']
        
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate items is a list
        if not isinstance(order_data['items'], list) or len(order_data['items']) == 0:
            raise ValueError("'items' must be a non-empty list")
        
        # ----------------------------------------
        # STEP 2: Generate Order ID
        # ----------------------------------------
        # Format: ORD-YYYYMMDD-XXXX
        # Example: ORD-20240115-a1b2
        today = datetime.utcnow().strftime('%Y%m%d')
        unique_part = uuid.uuid4().hex[:8]  # First 8 chars of UUID
        order_id = f"ORD-{today}-{unique_part}"
        
        # ----------------------------------------
        # STEP 3: Calculate Order Total
        # ----------------------------------------
        total = self._calculate_total(order_data['items'])
        
        # ----------------------------------------
        # STEP 4: Build Order Message
        # ----------------------------------------
        order_message = {
            # Order identification
            'order_id': order_id,
            
            # Customer information
            'customer_name': order_data['customer_name'],
            'email': order_data['email'],
            'shipping_address': order_data['shipping_address'],
            
            # Order details
            'items': order_data['items'],
            'item_count': len(order_data['items']),
            'total': total,
            
            # Order type (standard, express, prime)
            'type': order_data.get('order_type', 'standard'),
            
            # Order status
            'status': 'pending',
            
            # Special instructions
            'notes': order_data.get('notes', ''),
            
            # Timestamps
            'created_at': datetime.utcnow().isoformat(),
            
            # For demo: flag test orders
            'is_test': order_data.get('is_test', False)
        }
        
        # ----------------------------------------
        # STEP 5: Publish to Queue
        # ----------------------------------------
        message_id = self.rabbitmq.publish_message(order_message)
        
        # ----------------------------------------
        # STEP 6: Return Confirmation
        # ----------------------------------------
        return {
            'success': True,
            'order_id': order_id,
            'message_id': message_id,
            'total': total,
            'status': 'pending',
            'queue': 'orders',
            'message': f'Order {order_id} has been queued for processing'
        }
    
    def _calculate_total(self, items: List[Dict]) -> float:
        """
        Calculate the total price of all items
        
        Args:
            items: List of item dictionaries with 'price' and 'quantity'
        
        Returns:
            float: Total price rounded to 2 decimal places
        """
        total = 0.0
        
        for item in items:
            # Get price and quantity (default to 1 if not specified)
            price = float(item.get('price', 0))
            quantity = int(item.get('quantity', 1))
            
            # Add to total
            total += price * quantity
        
        # Round to 2 decimal places
        return round(total, 2)
    
    def create_test_orders(self, count: int = 5) -> List[Dict]:
        """
        Create multiple test orders for demo purposes
        
        This is useful for:
        - Populating the queue with sample data
        - Testing search/filter in QueueExplorer
        - Demonstrating batch operations
        
        Args:
            count: Number of test orders to create
        
        Returns:
            list: List of order confirmations
        """
        # Sample data for test orders
        sample_customers = [
            {'name': 'John Doe', 'email': 'john@example.com'},
            {'name': 'Jane Smith', 'email': 'jane@example.com'},
            {'name': 'Bob Wilson', 'email': 'bob@example.com'},
            {'name': 'Alice Brown', 'email': 'alice@example.com'},
            {'name': 'Test User', 'email': 'test@test.com'},  # Test account
        ]
        
        sample_products = [
            {'product': 'iPhone 15 Pro', 'price': 1199.00},
            {'product': 'MacBook Pro 14"', 'price': 1999.00},
            {'product': 'AirPods Pro', 'price': 249.00},
            {'product': 'iPad Air', 'price': 599.00},
            {'product': 'Apple Watch', 'price': 399.00},
        ]
        
        sample_addresses = [
            '123 Main St, New York, NY 10001',
            '456 Oak Ave, Los Angeles, CA 90001',
            '789 Pine Rd, Chicago, IL 60601',
            '321 Elm St, Houston, TX 77001',
            '654 Maple Dr, Phoenix, AZ 85001',
        ]
        
        order_types = ['standard', 'express', 'prime']
        
        results = []
        
        import random
        
        for i in range(count):
            # Pick random data
            customer = random.choice(sample_customers)
            
            # Generate 1-3 random items
            num_items = random.randint(1, 3)
            items = []
            for _ in range(num_items):
                product = random.choice(sample_products).copy()
                product['quantity'] = random.randint(1, 2)
                items.append(product)
            
            # Create order
            order_data = {
                'customer_name': customer['name'],
                'email': customer['email'],
                'items': items,
                'shipping_address': random.choice(sample_addresses),
                'order_type': random.choice(order_types),
                'is_test': True  # Flag as test order
            }
            
            # Submit order
            result = self.create_order(order_data)
            results.append(result)
            
            print(f"✅ Created test order {i+1}/{count}: {result['order_id']}")
        
        return results


# --------------------------------------------
# CONVENIENCE FUNCTIONS
# --------------------------------------------

def send_order(order_data: Dict) -> Dict:
    """
    Convenience function to send an order
    
    Usage:
        from app.producer import send_order
        result = send_order({...})
    """
    producer = OrderProducer()
    return producer.create_order(order_data)


def send_test_orders(count: int = 5) -> List[Dict]:
    """
    Convenience function to send test orders
    
    Usage:
        from app.producer import send_test_orders
        results = send_test_orders(10)
    """
    producer = OrderProducer()
    return producer.create_test_orders(count)
