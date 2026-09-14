# Authentication Flow

Understanding how authentication works with the DevPortal API.

## Overview

The DevPortal API uses **Bearer Token** authentication. You need to include your API key in the `Authorization` header of every request.

## Getting an API Key

1. Sign up for a DevPortal account
2. Navigate to **Settings → API Keys**
3. Click **Generate New Key**
4. Copy and store your key securely

!> **Security Warning**: Never expose your API key in client-side code or public repositories.

## Making Authenticated Requests

Include the API key in the `Authorization` header:

```http
GET /v2/users/me HTTP/1.1
Host: api.devportal.io
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### cURL Example

```bash
curl -X GET "https://api.devportal.io/v2/users/me" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### JavaScript Example

```javascript
const response = await fetch('https://api.devportal.io/v2/users/me', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
```

### Python Example

```python
import requests

response = requests.get(
    'https://api.devportal.io/v2/users/me',
    headers={
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    }
)
data = response.json()
```

## Token Expiration

API keys do not expire by default. However, you can set an expiration date when generating a key:

- **No expiration**: Key remains valid until revoked
- **Custom expiration**: Key expires after a set number of days
- **Rotation**: Generate a new key before the old one expires

## OAuth 2.0 Flow

For user-facing applications, use OAuth 2.0:

### Step 1: Redirect to Authorization URL

```
https://api.devportal.io/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=read write
```

### Step 2: Exchange Code for Token

```bash
curl -X POST "https://api.devportal.io/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "code": "AUTHORIZATION_CODE",
    "grant_type": "authorization_code",
    "redirect_uri": "YOUR_REDIRECT_URI"
  }'
```

### Step 3: Use the Access Token

```http
GET /v2/users/me HTTP/1.1
Host: api.devportal.io
Authorization: Bearer ACCESS_TOKEN
```

## Scopes

Control access with scopes:

| Scope | Description |
|-------|-------------|
| `read` | Read access to resources |
| `write` | Create and update resources |
| `delete` | Delete resources |
| `admin` | Full administrative access |

## Error Responses

### 401 Unauthorized

```json
{
  "error": "unauthorized",
  "message": "Invalid or missing API key",
  "status": 401
}
```

### 403 Forbidden

```json
{
  "error": "forbidden",
  "message": "Insufficient permissions for this resource",
  "status": 403
}
```

## Best Practices

1. **Store keys securely** - Use environment variables or a secrets manager
2. **Rotate keys regularly** - Generate new keys every 90 days
3. **Use minimal scopes** - Only request the permissions you need
4. **Monitor usage** - Check API logs for unusual activity
5. **Revoke compromised keys** - Immediately revoke any exposed keys
