# Users API (v2)

Manage users and their profiles.

## List Users

```http
GET /v2/users
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (max 100) |
| `status` | string | `all` | Filter by status: `active`, `inactive`, `all` |
| `created_after` | string | null | Filter by creation date (ISO 8601) |

### Response

```json
{
  "data": [
    {
      "id": "user_abc123",
      "email": "john@example.com",
      "name": "John Doe",
      "status": "active",
      "role": "admin",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-09-10T14:20:00Z"
    }
  ],
  "pagination": {
    "total": 50,
    "per_page": 20,
    "current_page": 1,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false,
    "next_cursor": "eyJpZCI6MjB9"
  }
}
```

## Get Current User

```http
GET /v2/users/me
```

### Response

```json
{
  "id": "user_abc123",
  "email": "john@example.com",
  "name": "John Doe",
  "status": "active",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-09-10T14:20:00Z",
  "preferences": {
    "timezone": "UTC",
    "language": "en",
    "theme": "light"
  }
}
```

## Get a User

```http
GET /v2/users/{id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | User ID |

### Response

```json
{
  "id": "user_abc123",
  "email": "john@example.com",
  "name": "John Doe",
  "status": "active",
  "role": "member",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-09-10T14:20:00Z"
}
```

## Update User

```http
PATCH /v2/users/{id}
```

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name |
| `email` | string | Email address |
| `status` | string | `active` or `inactive` |

```json
{
  "name": "John Smith",
  "email": "john.smith@example.com"
}
```

## Delete User

```http
DELETE /v2/users/{id}
```

### Response

```http
204 No Content
```
