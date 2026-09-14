# Pagination

The DevPortal API uses cursor-based pagination for listing resources.

## How It Works

API responses that return multiple items include pagination metadata:

```json
{
  "data": [
    { "id": "res_1", "name": "Resource 1" },
    { "id": "res_2", "name": "Resource 2" }
  ],
  "pagination": {
    "total": 100,
    "per_page": 20,
    "current_page": 1,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false,
    "next_cursor": "eyJpZCI6MjB9",
    "prev_cursor": null
  }
}
```

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (max 100) |
| `cursor` | string | null | Cursor for cursor-based pagination |

## Offset-Based Pagination

```bash
# Get page 1 (default)
curl "https://api.devportal.io/v2/resources?page=1&per_page=20" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Get page 3
curl "https://api.devportal.io/v2/resources?page=3&per_page=20" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Cursor-Based Pagination

```bash
# First request
curl "https://api.devportal.io/v2/resources?per_page=20" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Use next_cursor from response for next page
curl "https://api.devportal.io/v2/resources?per_page=20&cursor=eyJpZCI6MjB9" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## JavaScript Example

```javascript
async function fetchAllPages(baseUrl) {
  let allItems = [];
  let cursor = null;
  let hasNext = true;
  
  while (hasNext) {
    const params = new URLSearchParams({ per_page: '100' });
    if (cursor) params.set('cursor', cursor);
    
    const response = await fetch(`${baseUrl}?${params}`, {
      headers: { 'Authorization': 'Bearer YOUR_API_KEY' }
    });
    const data = await response.json();
    
    allItems = allItems.concat(data.data);
    cursor = data.pagination.next_cursor;
    hasNext = data.pagination.has_next;
  }
  
  return allItems;
}

// Usage
const allResources = await fetchAllPages('https://api.devportal.io/v2/resources');
console.log(`Fetched ${allResources.length} resources`);
```

## Python Example

```python
import requests

def fetch_all_pages(base_url, api_key):
    all_items = []
    cursor = None
    
    while True:
        params = {'per_page': 100}
        if cursor:
            params['cursor'] = cursor
        
        response = requests.get(
            base_url,
            headers={'Authorization': f'Bearer {api_key}'},
            params=params
        )
        data = response.json()
        
        all_items.extend(data['data'])
        
        if not data['pagination']['has_next']:
            break
        
        cursor = data['pagination']['next_cursor']
    
    return all_items
```

## Headers

Pagination info is also available in response headers:

```http
Link: <https://api.devportal.io/v2/resources?cursor=abc>; rel="next"
X-Total-Count: 100
X-Per-Page: 20
X-Current-Page: 1
```

## Sorting

Combine pagination with sorting:

```bash
curl "https://api.devportal.io/v2/resources?sort=-created_at&per_page=20" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Sort fields: `created_at`, `-created_at` (desc), `name`, `-name`, `updated_at`, `-updated_at`
