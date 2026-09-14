# Webhooks Guide

Webhooks allow your application to receive real-time notifications when events occur in DevPortal.

## Overview

Webhooks are HTTP POST requests sent to your server when specific events happen. Unlike polling, webhooks push data to you instantly.

## Supported Events

| Event | Description |
|-------|-------------|
| `resource.created` | A new resource was created |
| `resource.updated` | A resource was modified |
| `resource.deleted` | A resource was deleted |
| `user.created` | A new user signed up |
| `user.updated` | User profile was updated |
| `user.deleted` | User account was deleted |
| `api_key.created` | A new API key was generated |
| `api_key.revoked` | An API key was revoked |
| `webhook.created` | A webhook was registered |
| `webhook.updated` | A webhook was modified |
| `webhook.deleted` | A webhook was removed |

## Setting Up a Webhook

### Step 1: Create a Webhook Endpoint

Your endpoint must:
- Accept HTTP POST requests
- Return a 2xx status code within 5 seconds
- Be publicly accessible (HTTPS recommended)

### Step 2: Register the Webhook

```bash
curl -X POST "https://api.devportal.io/v2/webhooks" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/devportal",
    "events": ["resource.created", "resource.updated", "resource.deleted"],
    "secret": "your-webhook-secret",
    "active": true
  }'
```

### Step 3: Verify the Signature

Each webhook request includes a signature in the `X-Webhook-Signature` header. Verify it to ensure authenticity:

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(`sha256=${expected}`)
  );
}

// Express example
app.post('/webhooks/devportal', (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const payload = JSON.stringify(req.body);
  
  if (!verifyWebhookSignature(payload, signature, WEBHOOK_SECRET)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  const event = req.body;
  handleEvent(event);
  
  res.status(200).json({ received: true });
});
```

## Webhook Payload Structure

```json
{
  "id": "evt_abc123def456",
  "type": "resource.created",
  "created_at": "2024-09-14T10:00:00Z",
  "data": {
    "id": "res_xyz789",
    "name": "My Resource",
    "status": "active",
    "created_by": "user_123",
    "metadata": {}
  }
}
```

## Retry Policy

If your endpoint returns a non-2xx response, DevPortal retries with exponential backoff:

| Attempt | Delay |
|---------|-------|
| 1 | 1 second |
| 2 | 2 seconds |
| 3 | 4 seconds |
| 4 | 8 seconds |
| 5 | 16 seconds |
| 6 | 32 seconds |
| 7 | 64 seconds |
| 8 | 128 seconds |
| 9 | 256 seconds |
| 10 | 512 seconds |

After 10 failed attempts, the webhook is marked as `failed` and retries stop.

## Managing Webhooks

### List All Webhooks

```bash
curl "https://api.devportal.io/v2/webhooks" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Get a Specific Webhook

```bash
curl "https://api.devportal.io/v2/webhooks/{id}" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Update a Webhook

```bash
curl -X PUT "https://api.devportal.io/v2/webhooks/{id}" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": ["resource.created"],
    "active": false
  }'
```

### Delete a Webhook

```bash
curl -X DELETE "https://api.devportal.io/v2/webhooks/{id}" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Test a Webhook

Send a test event to verify your endpoint:

```bash
curl -X POST "https://api.devportal.io/v2/webhooks/{id}/test" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "resource.created"
  }'
```

## Best Practices

1. **Verify signatures** - Always validate the webhook signature
2. **Respond quickly** - Return 2xx immediately; process asynchronously
3. **Handle duplicates** - Use the event ID to deduplicate
4. **Log events** - Store webhook events for debugging
5. **Monitor failures** - Set up alerts for failed webhook deliveries
6. **Use HTTPS** - Always use HTTPS endpoints in production

## Troubleshooting

### Webhook Not Firing
- Check that the webhook is `active`
- Verify the event type is subscribed
- Check the webhook delivery logs

### Signature Verification Fails
- Ensure you're using the raw request body (not parsed JSON)
- Verify the secret matches what was set during registration
- Check for encoding issues (UTF-8)

### Timeout Errors
- Your endpoint must respond within 5 seconds
- Process the event asynchronously and return 200 immediately
- Use a queue system for heavy processing
