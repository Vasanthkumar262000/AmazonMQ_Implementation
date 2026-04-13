# 🔍 QueueExplorer Connection Guide

## How to Connect QueueExplorer to Amazon MQ (RabbitMQ)

---

## What is QueueExplorer?

QueueExplorer is a Windows application that lets you:
- **Browse** all messages in a queue
- **Search** messages by content
- **Filter** messages by headers
- **Delete** specific messages
- **Edit** message content
- **Move** messages between queues

This is exactly what AWS SQS FIFO cannot do!

---

## Step 1: Download QueueExplorer

1. Go to: https://www.cogin.com/mq/
2. Click **"Download"**
3. Choose **Standard** (free) or **Professional** (paid)
4. Install on Windows

**Note:** Professional version has more search/filter features.

---

## Step 2: Launch QueueExplorer

1. Open QueueExplorer
2. You'll see an empty workspace

---

## Step 3: Create New RabbitMQ Connection

1. Go to **File → Connect to server** (or press Ctrl+N)
2. Select **"RabbitMQ"** from the list
3. Click **OK**

---

## Step 4: Enter Connection Details

Fill in the connection form:

| Field | Value | Notes |
|-------|-------|-------|
| **Display name** | `Amazon MQ Demo` | Any name you like |
| **Host** | `b-xxxx.mq.us-east-1.amazonaws.com` | Your broker endpoint |
| **Port** | `5671` | SSL port for Amazon MQ |
| **Username** | `admin` | Your broker username |
| **Password** | `YourSecurePassword123!` | Your broker password |
| **Virtual host** | `/` | Default virtual host |
| **Use SSL** | ✅ **Checked** | Required for Amazon MQ |

---

## Step 5: Test Connection

1. Click **"Test"** button
2. You should see: "Connection successful!"
3. If it fails, check:
   - Security group allows port 5671
   - Credentials are correct
   - SSL is enabled

---

## Step 6: Connect

1. Click **"OK"** to save and connect
2. The connection will appear in the left panel
3. Expand it to see:
   - Exchanges
   - Queues
   - **orders** (your queue!)

---

## Step 7: Browse Messages

1. Click on the **"orders"** queue
2. Messages appear in the right panel
3. Each row shows one message

### Message List Columns

| Column | Description |
|--------|-------------|
| # | Message number in queue |
| Message ID | Unique identifier |
| Timestamp | When message was sent |
| Size | Message size in bytes |

---

## Step 8: View Message Content

1. Click on a message in the list
2. The bottom panel shows message body
3. Click **"JSON"** tab for formatted view

### What you'll see:

```json
{
  "order_id": "ORD-20240115-a1b2c3d4",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "items": [...],
  "total": 1497.00,
  "status": "pending"
}
```

---

## Step 9: Search/Filter Messages

### Basic Filter

1. Click the **filter icon** (funnel) in toolbar
2. Enter search text
3. Messages are filtered

### Professional Version - Advanced Filter

1. Right-click column header
2. Select **"Filter"**
3. Enter criteria:
   - `email CONTAINS "test"`
   - `total > 1000`
   - `status = "pending"`

---

## Step 10: Delete Messages

### Delete Single Message

1. Select the message
2. Press **Delete** key (or right-click → Delete)
3. Confirm deletion

### Delete Multiple Messages

1. Hold **Ctrl** and click multiple messages
2. Press **Delete**
3. Confirm deletion

### Delete Filtered Messages

1. Apply a filter (e.g., show only test orders)
2. Select all with **Ctrl+A**
3. Press **Delete**

---

## Demo Scenarios

### Scenario 1: Delete Test Orders

1. Filter by: `email CONTAINS "test"`
2. Select all test orders
3. Delete them
4. Show manager that only real orders remain

### Scenario 2: Delete Failed Orders

1. Filter by: `status = "failed"`
2. Review failed orders
3. Delete ones that can't be fixed

### Scenario 3: Find Specific Order

1. Search for order ID: `ORD-20240115`
2. View the order details
3. Decide to keep or delete

---

## Comparison: SQS vs QueueExplorer

| Action | AWS SQS FIFO | QueueExplorer + RabbitMQ |
|--------|--------------|--------------------------|
| Browse messages | ❌ Cannot | ✅ Full list |
| Search by content | ❌ Cannot | ✅ Search/filter |
| Delete specific message | ❌ Need ReceiptHandle | ✅ Click and delete |
| View message body | ❌ Must receive | ✅ Just click |
| Edit message | ❌ Cannot | ✅ Edit and save |

---

## Troubleshooting

### "Connection Failed" Error

1. Check host/port are correct
2. Ensure SSL is checked
3. Verify credentials
4. Check security group allows your IP

### "Access Refused" Error

1. Check username/password
2. Verify the user has admin access in RabbitMQ

### "Queue Not Found"

1. Make sure you've sent at least one message
2. Queue is created when first message is sent
3. Try running `python run_api.py` and send a test order

### Messages Not Showing

1. Consumer might be running and processing them
2. Stop the consumer: close the `run_consumer.py` window
3. Send new messages

---

## Tips for Demo

1. **Stop the consumer** during demo so messages stay in queue
2. **Send various orders** (test, express, prime) for variety
3. **Show the filter** to find specific orders
4. **Demonstrate delete** with test orders
5. **Refresh** (F5) to show messages are gone

---

## Screenshots to Capture for Presentation

1. QueueExplorer connected to Amazon MQ
2. List of messages in orders queue
3. JSON content of an order
4. Filter applied to show test orders
5. Before/after deletion (message count)

---

## Next Steps

After connecting QueueExplorer:
1. ✅ Send orders via Postman
2. ✅ View them in QueueExplorer
3. ✅ Practice search and delete
4. ✅ Prepare demo for manager
