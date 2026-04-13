"""
============================================
ORDER CONSUMER
============================================

This module handles consuming (processing) orders from the queue.

In a real e-commerce system, the consumer would:
- Validate payment
- Reserve inventory
- Create shipping labels
- Send confirmation emails
- Update database

For this demo, we just log the order and acknowledge it.

Consumer Concepts:
- Prefetch: How many messages to load at once
- Acknowledgment: Tell RabbitMQ we processed the message
- Reject/Requeue: Send message back if processing fails
- Dead Letter: Failed messages go to a separate queue
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# pika - RabbitMQ client
import pika

# json - Parse message body
import json

# time - For delays between retries
import time

# datetime - Timestamps
from datetime import datetime

# ssl - For secure connections
import ssl

# Import configuration
from app.config import Config


class OrderConsumer:
    """
    Order Consumer Class
    --------------------
    Consumes and processes orders from the RabbitMQ queue.
    
    This runs as a separate process from the API.
    It continuously listens for new messages and processes them.
    """
    
    def __init__(self):
        """
        Initialize the consumer
        
        Sets up connection parameters and state tracking.
        """
        # Connection state
        self.connection = None
        self.channel = None
        
        # Processing statistics
        self.processed_count = 0
        self.failed_count = 0
        self.start_time = None
        
        # Build connection parameters
        self.connection_params = self._build_connection_params()
    
    def _build_connection_params(self):
        """
        Build connection parameters
        
        Same as in rabbitmq_client.py but defined here
        so the consumer can run independently.
        """
        credentials = pika.PlainCredentials(
            username=Config.RABBITMQ_USERNAME,
            password=Config.RABBITMQ_PASSWORD
        )
        
        if Config.is_amazon_mq():
            ssl_context = ssl.create_default_context()
            ssl_options = pika.SSLOptions(ssl_context)
            
            return pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                virtual_host=Config.RABBITMQ_VHOST,
                credentials=credentials,
                ssl_options=ssl_options,
                heartbeat=600,
                blocked_connection_timeout=300
            )
        else:
            return pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                virtual_host=Config.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
    
    def connect(self):
        """
        Establish connection to RabbitMQ
        """
        print(f"🔌 Connecting to RabbitMQ at {Config.RABBITMQ_HOST}...")
        
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        
        # Declare queue (ensures it exists)
        self.channel.queue_declare(
            queue=Config.QUEUE_NAME,
            durable=True
        )
        
        # Set prefetch count
        # This limits how many messages are sent to this consumer at once
        # prefetch_count=1 means process one message at a time
        # This ensures fair distribution among multiple consumers
        self.channel.basic_qos(prefetch_count=1)
        
        print(f"✅ Connected! Listening on queue: {Config.QUEUE_NAME}")
    
    def process_order(self, order: dict) -> bool:
        """
        Process a single order
        
        This is where the actual business logic goes.
        In a real system, this would:
        - Charge the customer
        - Update inventory
        - Create shipping label
        - Send confirmation email
        
        Args:
            order: The order data dictionary
        
        Returns:
            bool: True if successful, False if failed
        """
        order_id = order.get('order_id', 'unknown')
        
        print(f"\n{'='*50}")
        print(f"📦 Processing Order: {order_id}")
        print(f"{'='*50}")
        print(f"   Customer: {order.get('customer_name', 'N/A')}")
        print(f"   Email:    {order.get('email', 'N/A')}")
        print(f"   Items:    {order.get('item_count', 0)} items")
        print(f"   Total:    ${order.get('total', 0):.2f}")
        print(f"   Type:     {order.get('type', 'standard')}")
        print(f"   Status:   {order.get('status', 'unknown')}")
        
        # ----------------------------------------
        # SIMULATE PROCESSING
        # ----------------------------------------
        # In a real system, this would do actual work
        # For demo, we just add a small delay
        
        try:
            # Simulate processing time (0.5 seconds)
            time.sleep(0.5)
            
            # Check if this is a "test" order that should fail
            # Useful for demonstrating dead letter queues
            if order.get('should_fail', False):
                raise Exception("Simulated failure for testing")
            
            # Update status
            order['status'] = 'processed'
            order['processed_at'] = datetime.utcnow().isoformat()
            
            print(f"✅ Order {order_id} processed successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Order {order_id} failed: {e}")
            return False
    
    def on_message(self, channel, method, properties, body):
        """
        Callback function called when a message is received
        
        This is the heart of the consumer. It's called automatically
        by Pika when a new message arrives.
        
        Args:
            channel: The channel object
            method: Delivery method (contains delivery_tag for ack/nack)
            properties: Message properties (headers, message_id, etc.)
            body: The actual message content (bytes)
        """
        try:
            # ----------------------------------------
            # STEP 1: Parse the message
            # ----------------------------------------
            # Body is bytes, need to decode to string then parse JSON
            order = json.loads(body.decode('utf-8'))
            
            # ----------------------------------------
            # STEP 2: Process the order
            # ----------------------------------------
            success = self.process_order(order)
            
            # ----------------------------------------
            # STEP 3: Acknowledge or Reject
            # ----------------------------------------
            if success:
                # ACK = Acknowledge
                # Tells RabbitMQ we processed the message successfully
                # RabbitMQ will remove the message from the queue
                channel.basic_ack(delivery_tag=method.delivery_tag)
                self.processed_count += 1
                
            else:
                # NACK = Negative Acknowledge
                # Tells RabbitMQ the message failed
                # requeue=False means don't put it back in the queue
                # It will go to the Dead Letter Queue instead
                channel.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False  # Send to DLQ
                )
                self.failed_count += 1
            
            # Print statistics
            print(f"📊 Stats: Processed={self.processed_count}, Failed={self.failed_count}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in message: {e}")
            # Reject malformed messages
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            self.failed_count += 1
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            # Reject on any other error
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            self.failed_count += 1
    
    def start_consuming(self):
        """
        Start consuming messages
        
        This runs forever (until interrupted) and processes
        messages as they arrive.
        """
        # Connect to RabbitMQ
        self.connect()
        
        # Record start time
        self.start_time = datetime.utcnow()
        
        # Register the callback function
        # basic_consume sets up the consumer to receive messages
        self.channel.basic_consume(
            queue=Config.QUEUE_NAME,
            on_message_callback=self.on_message
            # Note: auto_ack=False by default, so we manually ack/nack
        )
        
        # Print startup message
        print("\n" + "="*60)
        print("🚀 ORDER CONSUMER STARTED")
        print("="*60)
        print(f"   Queue:     {Config.QUEUE_NAME}")
        print(f"   Host:      {Config.RABBITMQ_HOST}")
        print(f"   Started:   {self.start_time.isoformat()}")
        print("="*60)
        print("   Waiting for orders... (Press Ctrl+C to stop)")
        print("="*60 + "\n")
        
        try:
            # start_consuming() blocks forever
            # It will call on_message() whenever a message arrives
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\n⚠️  Shutting down consumer...")
            self.channel.stop_consuming()
            
        finally:
            # Always close the connection
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            
            # Print final statistics
            print("\n" + "="*60)
            print("📊 CONSUMER STATISTICS")
            print("="*60)
            print(f"   Total Processed: {self.processed_count}")
            print(f"   Total Failed:    {self.failed_count}")
            print(f"   Runtime:         {datetime.utcnow() - self.start_time}")
            print("="*60 + "\n")


# --------------------------------------------
# MAIN ENTRY POINT
# --------------------------------------------
# This allows running the consumer directly:
# python -m app.consumer

if __name__ == '__main__':
    consumer = OrderConsumer()
    consumer.start_consuming()
