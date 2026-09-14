# SDK Usage Guide

Official SDKs for integrating with DevPortal.

## Official SDKs

=== "JavaScript/Node.js"
    ```bash
    npm install @itsPremkumar/devportal-js
    ```

    ```javascript
    import { DevPortal } from '@itsPremkumar/devportal-js';

    const client = new DevPortal({
      apiKey: process.env.DEVPORTAL_API_KEY,
      apiVersion: 'v2'
    });

    // List all resources
    const resources = await client.resources.list({
      per_page: 10
    });
    console.log(resources.data);

    // Create a resource
    const newResource = await client.resources.create({
      name: 'My Resource',
      type: 'compute',
      region: 'us-east-1'
    });
    console.log(newResource.data);

    // Get a specific resource
    const resource = await client.resources.get('res_abc123');
    console.log(resource.data);

    // Update a resource
    const updated = await client.resources.update('res_abc123', {
      name: 'Updated Name'
    });

    // Delete a resource
    await client.resources.delete('res_abc123');
    ```

=== "Python"
    ```bash
    pip install devportal-py
    ```

    ```python
    from devportal import Client

    client = Client(api_key="YOUR_API_KEY")

    # List resources
    resources = client.resources.list(per_page=10)
    for resource in resources.data:
        print(resource.name)

    # Create resource
    resource = client.resources.create(
        name="My Resource",
        type="compute",
        region="us-east-1"
    )
    print(resource.id)

    # Get resource
    resource = client.resources.get("res_abc123")
    print(resource.name)
    ```

=== "Go"
    ```bash
    go get github.com/itsPremkumar/devportal-go
    ```

    ```go
    import "github.com/itsPremkumar/devportal-go"

    client := devportal.NewClient("YOUR_API_KEY")

    // List resources
    resources, err := client.Resources.List(&devportal.ListParams{
      PerPage: 10,
    })
    if err != nil {
      log.Fatal(err)
    }
    for _, r := range resources.Data {
      fmt.Println(r.Name)
    }
    ```

## Authentication

All SDKs support API key authentication:

```javascript
// Via constructor
const client = new DevPortal({ apiKey: 'YOUR_KEY' });

// Via environment variable (automatic)
// Set DEVPORTAL_API_KEY in your environment
const client = new DevPortal();

// Override per request
const client = new DevPortal({ apiKey: 'KEY_1' });
const result = await client.resources.list({}, { apiKey: 'KEY_2' });
```

## Error Handling

All SDKs throw typed errors:

=== "JavaScript"
    ```javascript
    try {
      const resource = await client.resources.get('invalid_id');
    } catch (error) {
      if (error instanceof DevPortal.NotFoundError) {
        console.log('Resource not found');
      } else if (error instanceof DevPortal.AuthenticationError) {
        console.log('Invalid API key');
      } else if (error instanceof DevPortal.RateLimitError) {
        console.log(`Rate limited. Retry after ${error.retryAfter}s`);
      } else if (error instanceof DevPortal.ValidationError) {
        console.log('Validation errors:', error.details);
      } else {
        console.log('Unexpected error:', error);
      }
    }
    ```

=== "Python"
    ```python
    from devportal.errors import (
      NotFoundError, AuthenticationError,
      RateLimitError, ValidationError
    )

    try:
      resource = client.resources.get("invalid_id")
    except NotFoundError:
      print("Resource not found")
    except AuthenticationError:
      print("Invalid API key")
    except RateLimitError as e:
      print(f"Rate limited. Retry after {e.retry_after}s")
    except ValidationError as e:
      print(f"Validation errors: {e.details}")
    ```

## Pagination

SDKs handle pagination automatically:

```javascript
// Iterate all pages automatically
for await (const resource of client.resources.listAll()) {
  console.log(resource.name);
}

// Manual pagination
const page1 = await client.resources.list({ page: 1 });
if (page1.pagination.has_next) {
  const page2 = await client.resources.list({ page: 2 });
}
```

## Retries

SDKs automatically retry failed requests:

```javascript
const client = new DevPortal({
  apiKey: 'YOUR_KEY',
  maxRetries: 5,
  retryDelay: 1000,      // Initial delay in ms
  retryBackoff: 2         // Exponential backoff multiplier
});
```

## Webhook Verification

```javascript
const isValid = client.webhooks.verifySignature(
  payload,      // Raw request body string
  signature,    // X-Webhook-Signature header value
  secret        // Your webhook secret
);

if (!isValid) {
  throw new Error('Invalid webhook signature');
}
```

## TypeScript Support

All SDKs include full TypeScript definitions:

```typescript
import { DevPortal, Resource, ListResponse } from '@itsPremkumar/devportal-js';

const client = new DevPortal({ apiKey: 'KEY' });

const response: ListResponse<Resource> = await client.resources.list();
const resources: Resource[] = response.data;
```

## Rate Limiting

SDKs automatically respect rate limits:

```javascript
const client = new DevPortal({
  apiKey: 'KEY',
  respectRateLimits: true,  // Automatically wait when rate limited
  maxWaitTime: 60           // Max seconds to wait (default: 60)
});
```
