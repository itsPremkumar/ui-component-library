# Authentication (v2)

All API requests require authentication using an API key.

## Obtaining an API Key

1. Sign in to your DevPortal account
2. Go to **Settings → API Keys**
3. Click **Generate New Key**
4. Set a name and optional expiration
5. Copy the key immediately

!> **Important**: The key is shown only once. Store it securely.

## Using Your API Key

Include your API key in the `Authorization` header:

```http
GET /v2/users/me HTTP/1.1
Host: api.devportal.io
Authorization: Bearer sk_live_abc123...
Content-Type: application/json
```

## Authentication Errors

### Missing Key

```http
401 Unauthorized

{
  "error": "unauthorized",
  "message": "Missing API key. Include it in the Authorization header."
}
```

### Invalid Key

```http
401 Unauthorized

{
  "error": "unauthorized",
  "message": "Invalid API key"
}
```

### Revoked Key

```http
401 Unauthorized

{
  "error": "unauthorized",
  "message": "This API key has been revoked"
}
```

## OAuth 2.0

For user-facing applications:

1. Redirect user to `https://api.devportal.io/oauth/authorize`
2. User grants permission
3. Exchange the authorization code for a token
4. Use the access token in API requests

### Scopes

| Scope | Access |
|-------|--------|
| `read` | Read resources |
| `write` | Create/update resources |
| `delete` | Delete resources |
| `admin` | Full access |
