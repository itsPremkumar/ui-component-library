# Authentication (v1)

!> **Deprecated**: This is the v1 authentication endpoint. Use [v2 authentication](../v2/authentication.md) instead.

## API Key Authentication

Include your API key in every request:

```http
GET /v1/users HTTP/1.1
Host: api.devportal.io
X-API-Key: your_api_key_here
Content-Type: application/json
```

Note: v1 uses `X-API-Key` header instead of `Authorization: Bearer`.

## Response Errors

```json
{
  "error": "unauthorized",
  "message": "Invalid API key",
  "status": 401
}
```
