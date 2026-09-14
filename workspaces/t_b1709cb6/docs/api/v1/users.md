# Users API (v1)

!> **Deprecated**: This is the v1 users endpoint. Use [v2 users](../v2/users.md) instead.

## List Users

```http
GET /v1/users
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page |

### Response

```json
{
  "users": [
    {
      "id": "user_123",
      "email": "john@example.com",
      "name": "John Doe",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

## Get User

```http
GET /v1/users/{id}
```

### Response

```json
{
  "id": "user_123",
  "email": "john@example.com",
  "name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```
