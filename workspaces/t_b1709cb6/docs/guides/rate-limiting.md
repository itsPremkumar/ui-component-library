# Rate Limiting

The DevPortal API implements rate limiting to ensure fair usage and prevent abuse.

## Rate Limit Headers

Every API response includes rate limit headers:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1694700000
Content-Type: application/json
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per hour |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when the limit resets |

## Rate Limits by Plan

| Plan | Limit | Period |
|------|-------|--------|
| Free | 100 | per hour |
| Starter | 1,000 | per hour |
| Pro | 10,000 | per hour |
| Enterprise | 100,000 | per hour |

## Rate Limit Exceeded

When you exceed the rate limit, the API returns `429 Too Many Requests`:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 3600
Content-Type: application/json

{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit. Try again in 3600 seconds.",
  "retry_after": 3600
}
```

## Best Practices

### Implement Exponential Backoff

```javascript
async function fetchWithRetry(url, options = {}, maxRetries = 5) {
  let retries = 0;
  
  while (retries < maxRetries) {
    const response = await fetch(url, options);
    
    if (response.status !== 429) {
      return response;
    }
    
    const retryAfter = response.headers.get('Retry-After') || Math.pow(2, retries);
    await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
    retries++;
  }
  
  throw new Error('Max retries exceeded');
}
```

### Use Request Batching

Combine multiple operations into a single request when possible:

```javascript
// Bad: Multiple requests
const users = await fetch('/v2/users').then(r => r.json());
const resources = await fetch('/v2/resources').then(r => r.json());

// Good: Batch request
const data = await fetch('/v2/batch', {
  method: 'POST',
  body: JSON.stringify({ operations: [...] })
}).then(r => r.json());
```

### Cache Responses

Cache frequently accessed data locally:

```javascript
const cache = new Map();

async function getWithCache(url, ttl = 3600000) {
  const cached = cache.get(url);
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.data;
  }
  
  const response = await fetch(url, options);
  const data = await response.json();
  cache.set(url, { data, timestamp: Date.now() });
  return data;
}
```

## Endpoint-Specific Limits

Some endpoints have additional rate limits:

| Endpoint | Limit | Period |
|----------|-------|--------|
| `POST /v2/resources` | 100 | per minute |
| `DELETE /v2/resources/{id}` | 50 | per minute |
| `POST /v2/webhooks` | 10 | per minute |
| `POST /oauth/token` | 20 | per minute |

## Rate Limit Errors

### 429 Too Many Requests

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded",
  "retry_after": 120,
  "limit": 1000,
  "remaining": 0,
  "reset": 1694700000
}
```

### 503 Service Unavailable

Under extreme load, the API may return 503:

```json
{
  "error": "service_unavailable",
  "message": "Service temporarily unavailable. Please retry.",
  "retry_after": 300
}
```
