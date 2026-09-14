# API Reference

Welcome to the DevPortal API reference. This documentation covers all available endpoints across multiple API versions.

## API Versions

| Version | Status | Base URL |
|---------|--------|----------|
| v2 | **Latest** | `https://api.devportal.io/v2` |
| v1 | Legacy | `https://api.devportal.io/v1 |

!> **Deprecation Notice**: API v1 will be deprecated on **December 31, 2025**. Please migrate to v2.

## Base URL

=== "v2 (Latest)"
    ```
    https://api.devportal.io/v2
    ```

=== "v1 (Legacy)"
    ```
    https://api.devportal.io/v1
    ```

## Authentication

All API requests require authentication via Bearer token:

```http
Authorization: Bearer YOUR_API_KEY
```

## Common Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token |
| `Content-Type` | Yes | `application/json` |
| `Accept` | No | `application/json` |
| `Idempotency-Key` | No | Unique key for idempotent requests |

## Pagination

List endpoints support cursor-based pagination:

```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "per_page": 20,
    "has_next": true,
    "next_cursor": "eyJpZCI6MjB9"
  }
}
```

## Rate Limiting

Rate limits vary by plan:

| Plan | Limit | Period |
|------|-------|--------|
| Free | 100 | per hour |
| Starter | 1,000 | per hour |
| Pro | 10,000 | per hour |
| Enterprise | 100,000 | per hour |

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "status": 400,
  "details": [...]
}
```

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List users |
| GET | `/users/me` | Get current user |
| GET | `/users/{id}` | Get a user |
| GET | `/resources` | List resources |
| POST | `/resources` | Create a resource |
| GET | `/resources/{id}` | Get a resource |
| PUT | `/resources/{id}` | Update a resource |
| DELETE | `/resources/{id}` | Delete a resource |
| GET | `/webhooks` | List webhooks |
| POST | `/webhooks` | Create a webhook |
| DELETE | `/webhooks/{id}` | Delete a webhook |

Choose a version from the sidebar to view detailed endpoint documentation.
