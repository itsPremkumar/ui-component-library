# Webhooks API (v2)

Manage webhooks for real-time event notifications.

## List Webhooks

```http
GET /v2/webhooks
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active` | boolean | null | Filter by active status |
| `event_type` | string | null | Filter by event type |

### Response

```json
{
  "data": [
    {
      "id": "whk_abc123",
      "url": "https://myapp.com/webhooks",
      "events": ["resource.created", "resource.updated"],
      "active": true,
      "created_at": "2024-05-20T14:00:00Z",
      "last_triggered": "2024-09-14T09:30:00Z"
    }
  ],
  "pagination": {
    "total": 5,
    "per_page": 20,
    "has_next": false
  }
}
```

## Create Webhook

```http
POST /v2/webhooks
```

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Your webhook endpoint URL |
| `events` | array | Yes | List of event types to subscribe to |
| `secret` | string | No | Secret for HMAC signature verification |
| `active` | boolean | No | Default: `true` |

```json
{
  "url": "https://myapp.com/webhooks/devportal",
  "events": ["resource.created", "resource.deleted"],
  "secret": "whsec_abc123",
  "active": true
}
```

### Response

```json
{
  "id": "whk_new456",
  "url": "https://myapp.com/webhooks/devportal",
  "events": ["resource.created", "resource.deleted"],
  "active": true,
  "created_at": "2024-09-14T10:00:00Z",
  "last_triggered": null
}
```

## Get Webhook

```http
GET /v2/webhooks/{id}
```

### Response

```json
{
  "id": "whk_abc123",
  "url": "https://myapp.com/webhooks",
  "events": ["resource.created", "resource.updated"],
  "active": true,
  "created_at": "2024-05-20T14:00:00Z",
  "last_triggered": "2024-09-14T09:30:00Z"
}
```

## Update Webhook

```http
PATCH /v2/webhooks/{id}
```

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | New endpoint URL |
| `events` | array | Updated event subscriptions |
| `active` | boolean | Enable/disable the webhook |

```json
{
  "events": ["resource.created", "resource.updated", "resource.deleted"],
  "active": false
}
```

## Delete Webhook

```http
DELETE /v2/webhooks/{id}
```

### Response

```http
204 No Content
```

## Test Webhook

Send a test event to your endpoint:

```http
POST /v2/webhooks/{id}/test
```

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `event` | string | Event type to simulate |

```json
{
  "event": "resource.created"
}
```

## Available Events

| Event | Description |
|-------|-------------|
| `resource.created` | New resource created |
| `resource.updated` | Resource modified |
| `resource.deleted` | Resource deleted |
| `user.created` | New user registered |
| `user.updated` | User profile changed |
| `user.deleted` | User account removed |
| `api_key.created` | API key generated |
| `api_key.revoked` | API key revoked |

## Webhook Security

Every webhook request includes a signature header:

```
X-Webhook-Signature: sha256=abc123def456...
```

Verify it using HMAC-SHA256:

```javascript
const crypto = require('crypto');
const signature = crypto
  .createHmac('sha256', secret)
  .update(rawBody)
  'hex');
```
