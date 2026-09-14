# Error Handling

The DevPortal API uses standard HTTP status codes and returns detailed error information.

## HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded, no body returned |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "status": 400,
  "details": [
    {
      "field": "email",
      "message": "Must be a valid email address"
    }
  ],
  "request_id": "req_abc123def456",
  "documentation_url": "https://docs.devportal.io/errors/bad_request"
}
```

## Error Codes

### 400 - Bad Request

```json
{
  "error": "bad_request",
  "message": "Invalid JSON in request body",
  "status": 400
}
```

### 401 - Unauthorized

```json
{
  "error": "unauthorized",
  "message": "Invalid or missing API key",
  "status": 401
}
```

### 403 - Forbidden

```json
{
  "error": "forbidden",
  "message": "You do not have permission to access this resource",
  "status": 403
}
```

### 404 - Not Found

```json
{
  "error": "not_found",
  "message": "Resource not found",
  "status": 404
}
```

### 409 - Conflict

```json
{
  "error": "conflict",
  "message": "A resource with this identifier already exists",
  "status": 409
}
```

### 422 - Validation Error

```json
{
  "error": "validation_error",
  "message": "Request validation failed",
  "status": 422,
  "details": [
    {
      "field": "name",
      "message": "Name is required"
    },
    {
      "field": "email",
      "message": "Must be a valid email"
    }
  ]
}
```

### 429 - Rate Limit Exceeded

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again later.",
  "status": 429,
  "retry_after": 3600
}
```

### 500 - Internal Server Error

```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "status": 500,
  "request_id": "req_abc123def456"
}
```

## Handling Errors in Code

### JavaScript

```javascript
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY',
        ...options.headers
      }
    });

    if (!response.ok) {
      const error = await response.json();
      
      switch (response.status) {
        case 401:
          throw new AuthenticationError(error.message);
        case 404:
          throw new NotFoundError(error.message);
        case 429:
          throw new RateLimitError(error.message, error.retry_after);
        case 422:
          throw new ValidationError(error.message, error.details);
        default:
          throw new ApiError(error.message, response.status);
      }
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new NetworkError('Network request failed');
  }
}
```

### Python

```python
import requests

class ApiError(Exception):
    def __init__(self, message, status_code, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class ValidationError(ApiError):
    pass

class AuthenticationError(ApiError):
    pass

class NotFoundError(ApiError):
    pass

class RateLimitError(ApiError):
    def __init__(self, message, retry_after):
        self.retry_after = retry_after
        super().__init__(message, 429)

def api_request(method, url, **kwargs):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY',
        **kwargs.pop('headers', {})
    }
    
    response = requests.request(method, url, headers=headers, **kwargs)
    
    if not response.ok:
        error_data = response.json()
        message = error_data.get('message', 'Unknown error')
        
        if response.status_code == 401:
            raise AuthenticationError(message, 401)
        elif response.status_code == 404:
            raise NotFoundError(message, 404)
        elif response.status_code == 422:
            raise ValidationError(message, 422, error_data.get('details'))
        elif response.status_code == 429:
            raise RateLimitError(message, error_data.get('retry_after'))
        else:
            raise ApiError(message, response.status_code)
    
    return response.json()
```

## Idempotency

For safe retries, use the `Idempotency-Key` header:

```http
POST /v2/resources HTTP/1.1
Host: api.devportal.io
Authorization: Bearer YOUR_API_KEY
Idempotency-Key: unique-key-12345
Content-Type: application/json

{
  "name": "My Resource"
}
```

If you retry with the same key, the server returns the original response without creating a duplicate.
