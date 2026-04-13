#!/usr/bin/env python3
"""
============================================
RUN ORDER CONSUMER
============================================

This is the main entry point for the order consumer service.

Usage:
    python run_consumer.py

What it does:
1. Connects to RabbitMQ
2. Listens for messages on the 'orders' queue
3. Processes each order as it arrives
4. Acknowledges or rejects messages

Note for Demo:
--------------
During the demo, you may want to STOP the consumer
so that messages stay in the queue and can be viewed
in QueueExplorer.

The consumer processes messages immediately, so if
you want to accumulate messages for demonstration,
don't run this!
"""

# --------------------------------------------
# IMPORTS
# --------------------------------------------

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

# Import consumer
from app.consumer import OrderConsumer
from app.config import Config


def main():
    """
    Main function to start the consumer
    """
    # Print banner
    print("\n" + "="*60)
    print("📦 AMAZON MQ ORDER CONSUMER")
    print("="*60)
    
    # Print configuration
    Config.print_config()
    
    # Create and start consumer
    consumer = OrderConsumer()
    
    try:
        consumer.start_consuming()
    except KeyboardInterrupt:
        print("\n👋 Consumer stopped by user")
    except Exception as e:
        print(f"\n❌ Consumer error: {e}")
        raise


# --------------------------------------------
# ENTRY POINT
# --------------------------------------------

if __name__ == '__main__':
    main()
