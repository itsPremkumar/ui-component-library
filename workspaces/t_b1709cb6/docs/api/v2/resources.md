# Resources API (v2)

Resources are the core entities in DevPortal.

## List Resources

```http
GET /v2/resources
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (max 100) |
| `type` | string | null | Filter by resource type |
| `status` | string | `all` | Filter by status |
| `region` | string | null | Filter by region |

### Response

```json
{
  "data": [
    {
      "id": "res_xyz789",
      "name": "Production DB",
      "type": "database",
      "status": "active",
      "region": "us-east-1",
      "created_by": "user_abc123",
      "created_at": "2024-03-10T08:00:00Z",
      "updated_at": "2024-09-01T12:30:00Z",
      "metadata": {
        "engine": "postgresql",
        "version": "15.0"
      }
    }
  ],
  "pagination": {
    "total": 25,
    "per_page": 20,
    "has_next": true,
    "has_prev": false
  }
}
```

## Create Resource

```http
POST /v2/resources
```

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Resource name |
| `type` | string | Yes | Resource type |
| `region` | string | Yes | Deployment region |
| `status` | string | No | Default: `active` |
| `metadata` | object | No | Custom metadata |

```json
{
  "name": "Staging Server",
  "type": "compute",
  "region": "eu-west-1",
  "metadata": {
    "instance_type": "t3.medium",
    "os": "ubuntu-22.04"
  }
}
```

### Response

```json
{
  "id": "res_new123",
  "name": "Staging Server",
  "type": "compute",
  "status": "active",
  "region": "eu-west-1",
  "created_by": "user_abc123",
  "created_at": "2024-09-14T10:00:00Z",
  "updated_at": "2024-09-14T10:00:00Z",
  "metadata": {
    "instance_type": "t3.medium",
    "os": "ubuntu-22.04"
  }
}
```

## Get Resource

```http
GET /v2/resources/{id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Resource ID |

### Response

```json
{
  "id": "res_xyz789",
  "name": "Production DB",
  "type": "database",
  "status": "active",
  "region": "us-east-1",
  "created_by": "user_abc123",
  "created_at": "2024-03-10T08:00:00Z",
  "updated_at": "2024-09-01T12:30:00Z",
  "metadata": {
    "engine": "postgresql",
    "version": "15.0"
  }
}
```

## Update Resource

```http
PUT /v2/resources/{id}
```

### Request Body

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | New name |
| `status` | string | New status |
| `metadata` | object | Updated metadata |

```json
{
  "name": "Production Database",
  "metadata": {
    "engine": "postgresql",
    "version": "15.2"
  }
}
```

### Response

```json
{
  "id": "res_xyz789",
  "name": "Production Database",
  "type": "database",
  "status": "active",
  "region": "us-east-1",
  "updated_at": "2024-09-14T11:00:00Z",
  "metadata": {
    "engine": "postgresql",
    "version": "15.2"
  }
}
```

## Delete Resource

```http
DELETE /v2/resources/{id}
```

### Response

```http
204 No Content
```

## Resource Types

| Type | Description |
|------|-------------|
| `compute` | Virtual machines, containers |
| `database` | SQL and NoSQL databases |
| `storage` | Object storage, block storage |
| `network` | VPCs, load balancers, DNS |
| `ai` | ML models, inference endpoints |

## Status Values

| Status | Description |
|--------|-------------|
| `active` | Running and healthy |
| `inactive` | Stopped or paused |
| `pending` | Being created |
| `error` | Encountered an error |
| `deleting` | Being deleted |
