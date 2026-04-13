# 📘 AWS Amazon MQ Setup Guide

## Step-by-Step Instructions for Creating Amazon MQ (RabbitMQ) Broker

---

## Prerequisites

- AWS Account
- AWS Console access
- Basic understanding of VPC and Security Groups

---

## Step 1: Navigate to Amazon MQ

1. Log in to [AWS Console](https://console.aws.amazon.com)
2. Search for "Amazon MQ" in the search bar
3. Click on "Amazon MQ" service

![Amazon MQ in Console](https://docs.aws.amazon.com/images/amazon-mq/latest/developer-guide/images/amazon-mq-console.png)

---

## Step 2: Create a New Broker

1. Click **"Create broker"** button
2. Select **"RabbitMQ"** as the engine type
3. Click **"Next"**

---

## Step 3: Configure Broker Settings

### Basic Settings

| Setting | Value | Explanation |
|---------|-------|-------------|
| Broker name | `ecommerce-demo` | Unique name for your broker |
| Broker instance type | `mq.t3.micro` | Smallest (free tier eligible) |
| Deployment mode | `Single-instance broker` | For demo; use cluster for production |

### RabbitMQ Access

| Setting | Value | Explanation |
|---------|-------|-------------|
| Username | `admin` | Login username |
| Password | `YourSecurePassword123!` | Must be strong (8+ chars, mixed case, numbers, special) |

---

## Step 4: Configure Network

### Access Type

- ✅ Select **"Public accessibility"** (for demo)
- In production, use "Private accessibility" with VPN

### VPC Configuration

1. Select your **VPC**
2. Select a **public subnet**
3. Create a new **Security Group** or select existing

### Security Group Rules

Create these inbound rules:

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| Custom TCP | TCP | 5671 | 0.0.0.0/0 | AMQPS (SSL) connections |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Management Console |

---

## Step 5: Review and Create

1. Review all settings
2. Click **"Create broker"**
3. Wait 10-15 minutes for creation

---

## Step 6: Get Connection Details

Once the broker shows **"Running"** status:

1. Click on your broker name
2. Find the **"Connections"** section
3. Copy the **AMQPS endpoint**

Example endpoint:
```
amqps://b-1234abcd-5678-efgh-ijkl-9012mnopqrst.mq.us-east-1.amazonaws.com:5671
```

**Extract these values:**
- Host: `b-1234abcd-5678-efgh-ijkl-9012mnopqrst.mq.us-east-1.amazonaws.com`
- Port: `5671`

---

## Step 7: Access RabbitMQ Console

1. In broker details, find **"RabbitMQ web console"** URL
2. Click the link
3. Log in with your username/password

**Console URL format:**
```
https://b-xxxxxx.mq.us-east-1.amazonaws.com
```

---

## Step 8: Update .env File

Edit your `.env` file with the connection details:

```env
RABBITMQ_HOST=b-1234abcd-5678-efgh-ijkl-9012mnopqrst.mq.us-east-1.amazonaws.com
RABBITMQ_PORT=5671
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=YourSecurePassword123!
RABBITMQ_VHOST=/
```

---

## Troubleshooting

### Cannot Connect

1. **Check Security Group**: Ensure port 5671 is open
2. **Check Public Accessibility**: Must be enabled for external access
3. **Check Credentials**: Verify username/password in .env

### Connection Timeout

1. Check if broker is in "Running" state
2. Verify VPC/subnet has internet gateway
3. Check if your IP is blocked

### SSL Errors

1. Ensure you're using port 5671 (not 5672)
2. Python's ssl module should handle certificates automatically

---

## Cost Estimate

| Instance Type | Monthly Cost (approx) |
|---------------|----------------------|
| mq.t3.micro | ~$20/month |
| mq.m5.large | ~$150/month |

**Note:** You can stop the broker when not in use to save costs.

---

## Cleanup (After Demo)

To avoid charges, delete the broker:

1. Go to Amazon MQ console
2. Select your broker
3. Click **Actions → Delete**
4. Confirm deletion

---

## Next Steps

After setting up Amazon MQ:
1. ✅ Update `.env` file with credentials
2. ✅ Run `python run_api.py`
3. ✅ Test with Postman
4. ✅ Connect QueueExplorer
