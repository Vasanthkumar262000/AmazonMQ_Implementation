# 🎬 Demo Script for Manager

## "Search and Delete in Message Queues: AWS SQS vs Amazon MQ"

**Duration:** 10-15 minutes

---

## 🎯 Key Points to Demonstrate

1. **The Problem:** SQS FIFO cannot search or delete specific messages
2. **The Solution:** Amazon MQ (RabbitMQ) with QueueExplorer
3. **Live Demo:** Send orders, browse queue, search, and delete

---

## 📋 Pre-Demo Checklist

- [ ] Amazon MQ broker is running
- [ ] Flask API is running (`python run_api.py`)
- [ ] Consumer is **STOPPED** (so messages stay in queue)
- [ ] QueueExplorer is connected
- [ ] Postman is open with collection imported
- [ ] Queue is empty (or has a few messages)

---

## 🎤 Demo Script

### Introduction (2 minutes)

> "Today I want to show you a solution to a problem we've been facing with our message queues. When orders pile up in our SQS FIFO queue, we can't easily find and delete specific messages. Let me demonstrate how Amazon MQ with RabbitMQ solves this."

**Show this slide/diagram:**

```
Current Problem (SQS FIFO):
┌─────────────────────────────────────────┐
│  Orders Queue (1000s of messages)       │
│  ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐ │
│  │ ? │ ? │ ? │ ? │ ? │ ? │ ? │ ? │ ? │ │
│  └───┴───┴───┴───┴───┴───┴───┴───┴───┘ │
│                                         │
│  ❌ Cannot see what's inside            │
│  ❌ Cannot search for specific orders   │
│  ❌ Cannot delete test/invalid orders   │
│  ❌ Can only receive next 10 messages   │
└─────────────────────────────────────────┘
```

---

### Part 1: Show the Architecture (2 minutes)

> "Here's our new architecture using Amazon MQ:"

**Show this diagram:**

```
Solution (Amazon MQ + QueueExplorer):
┌─────────────┐      ┌─────────────┐      ┌─────────────────────┐
│   Postman   │─────▶│  Flask API  │─────▶│     Amazon MQ       │
│   (Orders)  │      │             │      │     (RabbitMQ)      │
└─────────────┘      └─────────────┘      │                     │
                                          │  ✅ Browse messages │
┌───────────────────────────────────┐     │  ✅ Search content  │
│         QueueExplorer             │◀────│  ✅ Delete specific │
│    (Management Tool)              │     │  ✅ Full visibility │
└───────────────────────────────────┘     └─────────────────────┘
```

> "Amazon MQ is managed by AWS, just like SQS. We don't manage servers. But it gives us full access to browse and manage our messages."

---

### Part 2: Live Demo - Send Orders (3 minutes)

> "Let me show you how this works in practice."

**Step 1: Show the API is running**

```
# Terminal should show:
🚀 AMAZON MQ DEMO API
✅ RabbitMQ connected!
🌐 STARTING WEB SERVER
   URL: http://localhost:5000
```

**Step 2: Send orders via Postman**

1. Open Postman
2. Send "Create Single Order" request

> "When a customer places an order on our website, it goes to our API and gets published to the queue."

3. Show the response:
```json
{
    "success": true,
    "order_id": "ORD-20240115-a1b2c3d4",
    "message_id": "...",
    "total": 1697.00,
    "status": "pending"
}
```

4. Send "Create Test Order" request (the one with test@test.com)

> "This is a test order that we might want to delete later."

5. Send "Create Batch Orders" to add 10 more

> "Now we have about 12 orders in the queue. Let's see them in QueueExplorer."

---

### Part 3: Live Demo - Browse Queue (2 minutes)

> "Now let me show you something you CANNOT do with SQS..."

**Step 1: Open QueueExplorer**

1. Show the connected Amazon MQ
2. Expand to see the `orders` queue
3. Click on the queue

> "Here we can see ALL messages in the queue. Not just 10, but ALL of them. With SQS, you can only receive up to 10 at a time, and you can't see them without consuming them."

**Step 2: Click on a message**

1. Show the message details panel
2. Switch to JSON view

> "We can see the complete order details - customer name, items, total, everything. Without consuming the message."

---

### Part 4: Live Demo - Search and Filter (2 minutes)

> "Now here's the powerful part - searching."

**Step 1: Apply a filter**

1. Click filter icon or use search
2. Type "test" to filter

> "I'm filtering to show only messages containing 'test'. These are test orders that shouldn't be processed."

**Step 2: Show filtered results**

> "You can see the test order we created. In a real scenario, we might have test orders, cancelled orders, or orders with invalid data that we need to remove."

**Alternative filter examples:**
- `order_type: express` - Show only express orders
- `total > 1000` - Show high-value orders
- `email: test@` - Show test accounts

---

### Part 5: Live Demo - Delete Specific Messages (2 minutes)

> "Now watch this - the main feature we've been missing."

**Step 1: Select the test order**

1. Click on the filtered test order

**Step 2: Delete it**

1. Press Delete key or right-click → Delete
2. Confirm deletion

> "The test order is now GONE. Permanently deleted from the queue. The consumer will never see it, and it won't be processed."

**Step 3: Verify deletion**

1. Clear the filter
2. Show remaining messages

> "See? 11 messages now instead of 12. The test order is completely removed."

**Step 4: Show Queue Stats (optional)**

1. Go to Postman
2. Send "Queue Statistics" request
3. Show message_count is reduced

---

### Part 6: Comparison Summary (1 minute)

> "Let me summarize the key differences:"

| Capability | SQS FIFO | Amazon MQ |
|------------|----------|-----------|
| Browse all messages | ❌ | ✅ |
| Search by content | ❌ | ✅ |
| Delete specific message | ❌ | ✅ |
| GUI Management Tool | ❌ | ✅ |
| Managed by AWS | ✅ | ✅ |
| Auto-scaling | ✅ | ⚠️ Manual sizing |

> "Both are managed by AWS. Amazon MQ requires us to choose an instance size, but gives us full visibility and control over our messages."

---

### Conclusion (1 minute)

> "With this approach, when our backend goes down and orders pile up, we can:
>
> 1. **See** exactly what's in the queue
> 2. **Find** problematic orders (test accounts, duplicates, invalid data)
> 3. **Delete** them without processing
> 4. **Keep** only valid orders for processing
>
> This saves engineering time and prevents invalid orders from causing issues downstream."

---

## ❓ Expected Questions and Answers

### Q: "Is Amazon MQ expensive?"

> "The smallest instance (mq.t3.micro) costs about $20/month. Compare this to developer time spent debugging queue issues - it pays for itself."

### Q: "Do we need to rewrite all our code?"

> "Yes, there are code changes needed. The demo project I've created shows exactly what the new code looks like. The main change is switching from boto3/SQS to pika/RabbitMQ."

### Q: "What about reliability?"

> "Amazon MQ has the same 99.9% SLA as SQS. For production, we'd use a multi-AZ cluster for high availability."

### Q: "Can we migrate gradually?"

> "Yes! We can run both systems in parallel during migration. New services use Amazon MQ while we migrate existing ones."

---

## 🎁 Handoff Materials

After the demo, share:

1. **This project code** - Complete working example
2. **AWS setup guide** - How to create Amazon MQ
3. **QueueExplorer guide** - How to connect and use
4. **Cost estimate** - Instance pricing comparison

---

## 📝 Notes for Presenter

- Keep the consumer **stopped** during demo so messages stay visible
- Have a backup plan if AWS is slow (show screenshots)
- Practice the flow 2-3 times before the meeting
- Have the Postman collection pre-configured
- Keep QueueExplorer connected before the demo starts
