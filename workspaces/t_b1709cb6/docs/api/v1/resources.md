# Resources API (v1)

!> **Deprecated**: This is the v1 resources endpoint. Use [v2 resources](../v2/resources.md) instead.

## List Resources

```http
GET /v1/resources
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page |

### Response

```json
{
  "resources": [
    {
      "id": "res_456",
      "name": "My Resource",
      "type": "server",
      "status": "active",
      "created_at": "2024-03-10T08:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 20
}
```

## Create Resource

```http
POST /v1/resources
```

### Request Body

```json
{
  "name": "New Resource",
  "type": "server"
}
```

### Response

```json
{
  "id": "res_789",
  "name": "New Resource",
  "type": "server",
  "status": "active",
  "created_at": "2024-09-14T10:00:00Z"
}
```

## Get Resource

```http
GET /v1/resources/{id}
```

### Response

```json
{
  "id": "res_456",
  "name": "My Resource",
  "type": "server",
  "status": "active",
  "created_at": "2024-03-10T08:00:00Z"
}
```

## Delete Resource

```http
DELETE /v1/resources/{id}
```

### Response

```http
204 No Content
```
