# 🚀 Amazon MQ (RabbitMQ) Demo Project

## E-Commerce Order Queue System

This project demonstrates how to use **Amazon MQ (Managed RabbitMQ)** for message queuing with the ability to **search and delete specific messages** using QueueExplorer.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Create Amazon MQ Broker](#phase-1-create-amazon-mq-broker)
4. [Phase 2: Project Setup](#phase-2-project-setup)
5. [Phase 3: Run the Application](#phase-3-run-the-application)
6. [Phase 4: Test with Postman](#phase-4-test-with-postman)
7. [Phase 5: Connect QueueExplorer](#phase-5-connect-queueexplorer)
8. [Phase 6: Demo Script for Manager](#phase-6-demo-script-for-manager)

---

## 🎯 Project Overview

### What This Demo Shows

1. **Send Orders via REST API** → Orders are published to RabbitMQ queue
2. **Messages Stored in Queue** → Amazon MQ holds messages until processed
3. **Browse Messages** → View all pending orders in RabbitMQ Console
4. **Search & Delete** → Use QueueExplorer to find and delete specific orders

### Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────────────┐
│   POSTMAN   │─────▶│  FLASK API  │─────▶│     AMAZON MQ       │
│             │ HTTP │  Port 5000  │ AMQP │    (RabbitMQ)       │
└─────────────┘      └─────────────┘      │                     │
                                          │  ┌───────────────┐  │
┌─────────────────────────────────────┐   │  │ orders queue  │  │
│         QUEUE EXPLORER              │◀──│  └───────────────┘  │
│  • Browse all messages              │   │                     │
│  • Search by content                │   └─────────────────────┘
│  • Delete specific messages         │
└─────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Software

| Software | Purpose | Download |
|----------|---------|----------|
| Python 3.9+ | Run the API | https://python.org |
| Postman | Test API endpoints | https://postman.com |
| QueueExplorer | Browse/delete messages | https://cogin.com/mq |
| AWS Account | Host Amazon MQ | https://aws.amazon.com |

### AWS Requirements

- AWS Account with permissions to create Amazon MQ brokers
- VPC with public subnet (for demo purposes)
- Security Group allowing ports 5671 (AMQPS) and 443 (Console)

---

## 🔧 Phase 1: Create Amazon MQ Broker

### Step 1.1: Go to Amazon MQ Console

1. Log in to AWS Console
2. Search for "Amazon MQ"
3. Click "Create broker"

### Step 1.2: Configure Broker

| Setting | Value |
|---------|-------|
| Engine type | **RabbitMQ** |
| Deployment mode | **Single-instance broker** (for demo) |
| Broker name | `ecommerce-demo` |
| Instance type | `mq.t3.micro` (free tier eligible) |
| RabbitMQ version | Latest (e.g., 3.13) |

### Step 1.3: Configure Access

| Setting | Value |
|---------|-------|
| Username | `admin` |
| Password | `YourSecurePassword123!` |
| Public accessibility | **Yes** (for demo only!) |

### Step 1.4: Configure Network

- Select your VPC
- Select public subnet
- Create or select security group with:
  - Inbound: Port 5671 (AMQPS) from 0.0.0.0/0
  - Inbound: Port 443 (HTTPS Console) from 0.0.0.0/0

### Step 1.5: Create Broker

- Click "Create broker"
- Wait 10-15 minutes for broker to be ready
- Note down the endpoint URL (e.g., `b-xxxx-xxxx.mq.us-east-1.amazonaws.com`)

---

## 💻 Phase 2: Project Setup

### Step 2.1: Clone/Download Project

```bash
# Create project directory
mkdir amazon-mq-demo
cd amazon-mq-demo
```

### Step 2.2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 2.3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2.4: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your Amazon MQ credentials
```

---

## ▶️ Phase 3: Run the Application

### Start the API Server

```bash
python run_api.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Connected to RabbitMQ successfully!
```

### (Optional) Start the Consumer

In a new terminal:
```bash
python run_consumer.py
```

---

## 📬 Phase 4: Test with Postman

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders` | Create new order |
| GET | `/api/orders` | List recent orders |
| GET | `/api/health` | Check API and RabbitMQ health |
| GET | `/api/queue/stats` | Get queue statistics |

### Send Order Request

**POST** `http://localhost:5000/api/orders`

```json
{
    "customer_name": "John Doe",
    "email": "john@example.com",
    "items": [
        {"product": "iPhone 15", "quantity": 1, "price": 999.00},
        {"product": "AirPods Pro", "quantity": 2, "price": 249.00}
    ],
    "shipping_address": "123 Main St, New York, NY 10001"
}
```

---

## 🔍 Phase 5: Connect QueueExplorer

### Step 5.1: Download QueueExplorer

1. Go to https://www.cogin.com/mq/
2. Download QueueExplorer (Standard or Professional)
3. Install on Windows

### Step 5.2: Create New Connection

1. Open QueueExplorer
2. Click **File → Connect to RabbitMQ**
3. Enter connection details:

| Field | Value |
|-------|-------|
| Host | `b-xxxx.mq.us-east-1.amazonaws.com` |
| Port | `5671` |
| Username | `admin` |
| Password | `YourSecurePassword123!` |
| Use SSL | ✅ Yes |
| Virtual Host | `/` |

### Step 5.3: Browse Messages

1. Expand the connection
2. Click on `orders` queue
3. View all messages in the list

### Step 5.4: Search and Delete

1. Use the filter bar to search
2. Select messages to delete
3. Press Delete key or click Delete button

---

## 🎬 Phase 6: Demo Script for Manager

See `docs/DEMO_SCRIPT.md` for a complete step-by-step demo script.

---

## 📁 Project Files

```
amazon-mq-demo/
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── run_api.py                # Start API server
├── run_consumer.py           # Start consumer
├── app/
│   ├── __init__.py          # Flask app
│   ├── config.py            # Configuration
│   ├── rabbitmq_client.py   # RabbitMQ connection
│   ├── producer.py          # Send messages
│   ├── consumer.py          # Process messages
│   └── routes.py            # API endpoints
└── postman/
    └── collection.json       # Postman collection
```

---

## 🆘 Troubleshooting

### Cannot connect to Amazon MQ

1. Check security group allows port 5671
2. Verify broker is in "Running" state
3. Check credentials in .env file

### Messages not appearing in queue

1. Check API response for errors
2. Verify RabbitMQ connection in health endpoint
3. Check consumer is not running (it will process messages)

---

## 📞 Support

For questions about this demo project, contact: [Your Email]
