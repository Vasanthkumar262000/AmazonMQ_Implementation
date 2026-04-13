"""
============================================
RABBITMQ CLIENT
============================================

This file handles all communication with RabbitMQ (Amazon MQ).
It provides a clean interface for connecting, publishing, and consuming messages.

Key Concepts:
- Connection: TCP connection to RabbitMQ server
- Channel: Virtual connection within the connection (for operations)
- Exchange: Routes messages to queues
- Queue: Stores messages until they're consumed
- Message: The data being sent

Amazon MQ Specifics:
- Uses SSL/TLS for secure connections (port 5671)
- Requires authentication
- Managed by AWS (patching, backups, etc.)
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# pika - Official RabbitMQ client for Python
import pika

# ssl - Python's SSL/TLS support for secure connections
import ssl

# json - For encoding/decoding message payloads
import json

# datetime - For timestamps in messages
from datetime import datetime

# uuid - For generating unique message IDs
import uuid

# Import our configuration
from app.config import Config


class RabbitMQClient:
    """
    RabbitMQ Client Class
    ---------------------
    Handles all RabbitMQ operations:
    - Establishing connections
    - Publishing messages to queues
    - Consuming messages from queues
    - Queue management (declare, purge, stats)
    
    Usage:
        client = RabbitMQClient()
        client.publish_message({'order_id': '123'})
    """
    
    def __init__(self):
        """
        Initialize the RabbitMQ client
        
        Sets up connection parameters but doesn't connect yet.
        Connection is established when needed (lazy connection).
        """
        # Store configuration values
        self.host = Config.RABBITMQ_HOST
        self.port = Config.RABBITMQ_PORT
        self.username = Config.RABBITMQ_USERNAME
        self.password = Config.RABBITMQ_PASSWORD
        self.vhost = Config.RABBITMQ_VHOST
        self.queue_name = Config.QUEUE_NAME
        
        # Connection and channel (initialized later)
        self.connection = None
        self.channel = None
        
        # Build connection parameters
        self.connection_params = self._build_connection_params()
    
    def _build_connection_params(self):
        """
        Build Pika connection parameters
        
        This creates the configuration object for connecting to RabbitMQ.
        
        For Amazon MQ:
        - SSL is required (port 5671)
        - TLS 1.2 or higher
        
        For local RabbitMQ:
        - No SSL needed (port 5672)
        
        Returns:
            pika.ConnectionParameters: Configuration for connection
        """
        # Create credentials object
        # This holds username and password for authentication
        credentials = pika.PlainCredentials(
            username=self.username,
            password=self.password
        )
        
        # Check if we need SSL (Amazon MQ)
        if Config.is_amazon_mq():
            # --------------------------------------------
            # SSL CONFIGURATION FOR AMAZON MQ
            # --------------------------------------------
            
            # Create SSL context with secure defaults
            # This configures TLS encryption for the connection
            ssl_context = ssl.create_default_context()
            
            # Create SSL options for Pika
            ssl_options = pika.SSLOptions(ssl_context)
            
            # Build connection parameters with SSL
            params = pika.ConnectionParameters(
                host=self.host,           # Amazon MQ endpoint
                port=self.port,           # 5671 for SSL
                virtual_host=self.vhost,  # Usually '/'
                credentials=credentials,  # Username/password
                ssl_options=ssl_options,  # SSL configuration
                
                # Heartbeat - sends periodic pings to keep connection alive
                # 600 seconds = 10 minutes
                heartbeat=600,
                
                # Blocked connection timeout
                # How long to wait if RabbitMQ is blocking connections
                blocked_connection_timeout=300
            )
        else:
            # --------------------------------------------
            # NON-SSL CONFIGURATION FOR LOCAL RABBITMQ
            # --------------------------------------------
            params = pika.ConnectionParameters(
                host=self.host,           # Usually 'localhost'
                port=self.port,           # 5672 for non-SSL
                virtual_host=self.vhost,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
        
        return params
    
    def connect(self):
        """
        Establish connection to RabbitMQ
        
        Creates a blocking connection (synchronous).
        Also sets up the channel and declares the queue.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            Exception: If connection fails
        """
        try:
            print(f"Connecting to RabbitMQ at {self.host}:{self.port}...")
            
            # Create blocking connection
            # "Blocking" means operations wait for completion before returning
            self.connection = pika.BlockingConnection(self.connection_params)
            
            # Create channel
            # A channel is a virtual connection inside the TCP connection
            # Most operations happen on channels, not the connection directly
            self.channel = self.connection.channel()
            
            # Declare the main queue
            # declare = create if not exists, verify if exists
            self._declare_queues()
            
            print(f"✅ Connected to RabbitMQ successfully!")
            print(f"   Queue '{self.queue_name}' is ready")
            
            return True
            
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error connecting to RabbitMQ: {e}")
            raise
    
    def _declare_queues(self):
        """
        Declare queues in RabbitMQ
        
        Declaring a queue:
        - Creates it if it doesn't exist
        - Verifies configuration if it exists
        
        Queue Options:
        - durable=True: Queue survives broker restart
        - arguments: Additional queue configuration
        """
        # Declare Dead Letter Exchange (DLX)
        # Failed messages are sent here
        self.channel.exchange_declare(
            exchange='dlx',           # Exchange name
            exchange_type='direct',   # Direct routing
            durable=True              # Survives restart
        )
        
        # Declare Dead Letter Queue
        self.channel.queue_declare(
            queue=Config.DLQ_NAME,
            durable=True
        )
        
        # Bind DLQ to DLX
        self.channel.queue_bind(
            queue=Config.DLQ_NAME,
            exchange='dlx',
            routing_key='failed'
        )
        
        # Declare main orders queue
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,  # Queue persists after broker restart
            arguments={
                # Dead letter configuration
                # Failed messages go to 'dlx' exchange with key 'failed'
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': 'failed',
                
                # Message TTL (optional) - messages expire after 24 hours
                # 'x-message-ttl': 86400000  # milliseconds
            }
        )
        
        print(f"   Queues declared: {self.queue_name}, {Config.DLQ_NAME}")
    
    def publish_message(self, message: dict) -> str:
        """
        Publish a message to the queue
        
        This is the main method for sending orders to the queue.
        
        Args:
            message: Dictionary containing the message data
                     Example: {'order_id': 'ORD-123', 'items': [...]}
        
        Returns:
            str: The unique message ID
            
        What happens:
        1. Generate unique message ID
        2. Add metadata (timestamp, etc.)
        3. Convert to JSON
        4. Publish to queue
        """
        # Ensure we're connected
        if not self.channel or self.connection.is_closed:
            self.connect()
        
        # Generate unique message ID
        # UUID4 generates a random unique identifier
        message_id = str(uuid.uuid4())
        
        # Add metadata to message
        message['_metadata'] = {
            'message_id': message_id,
            'timestamp': datetime.utcnow().isoformat(),
            'queue': self.queue_name
        }
        
        # Convert message to JSON string
        # RabbitMQ sends bytes, so we need to encode the JSON
        message_body = json.dumps(message)
        
        # Create message properties
        properties = pika.BasicProperties(
            # Delivery mode 2 = persistent
            # Message survives broker restart (if queue is durable)
            delivery_mode=2,
            
            # Content type helps consumers know how to parse
            content_type='application/json',
            
            # Unique ID for this message
            message_id=message_id,
            
            # Timestamp (UNIX epoch)
            timestamp=int(datetime.utcnow().timestamp()),
            
            # Custom headers for filtering in QueueExplorer
            headers={
                'order_id': message.get('order_id', 'unknown'),
                'customer_email': message.get('email', 'unknown'),
                'order_type': message.get('type', 'standard')
            }
        )
        
        # Publish the message
        self.channel.basic_publish(
            exchange='',              # Default exchange
            routing_key=self.queue_name,  # Queue name as routing key
            body=message_body,        # The actual message content
            properties=properties     # Message metadata
        )
        
        print(f"📤 Published message: {message_id}")
        
        return message_id
    
    def get_queue_stats(self) -> dict:
        """
        Get statistics about the queue
        
        Returns:
            dict: Queue statistics including:
                - message_count: Number of messages in queue
                - consumer_count: Number of active consumers
        """
        # Ensure we're connected
        if not self.channel or self.connection.is_closed:
            self.connect()
        
        # Passive declare = just get info, don't create
        # This returns queue information
        result = self.channel.queue_declare(
            queue=self.queue_name,
            passive=True  # Don't create, just check
        )
        
        return {
            'queue_name': self.queue_name,
            'message_count': result.method.message_count,
            'consumer_count': result.method.consumer_count
        }
    
    def close(self):
        """
        Close the connection to RabbitMQ
        
        Always call this when done to free resources.
        """
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 RabbitMQ connection closed")


# --------------------------------------------
# SINGLETON INSTANCE
# --------------------------------------------
# Create a single instance to be shared across the application
# This avoids creating multiple connections

_client_instance = None

def get_rabbitmq_client() -> RabbitMQClient:
    """
    Get the RabbitMQ client instance (Singleton pattern)
    
    This ensures we only have one connection to RabbitMQ
    across the entire application.
    
    Returns:
        RabbitMQClient: The shared client instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = RabbitMQClient()
        _client_instance.connect()
    
    return _client_instance
