# API Console

The DevPortal API Console lets you test API endpoints directly from your browser.

## Getting Started

1. Navigate to the **API Console** in the sidebar
2. Select an API version (v1 or v2)
3. Choose an endpoint from the dropdown
4. Fill in any required parameters
5. Click **Execute**

## Features

- **Version Switching** - Toggle between v1 and v2 endpoints
- **Parameter Input** - Fill in path, query, and body parameters
- **Response Viewer** - See formatted JSON responses with status codes
- **Request History** - View previous requests in the session
- **Copy Response** - One-click copy of response data

## Using the Console

### Selecting an Endpoint

Choose from the dropdown menu. Each entry shows:
- HTTP method (GET, POST, PUT, DELETE)
- Endpoint path
- Brief description

### Filling Parameters

Parameters are automatically detected from the endpoint definition:
- **Path parameters** - Fill in values for `{id}` placeholders
- **Query parameters** - Add optional query string values
- **Request body** - Enter JSON for POST/PUT requests

### Reading Responses

The response section shows:
- **Status code** - Color-coded (green for 2xx, red for errors)
- **Response body** - Formatted and syntax-highlighted JSON
- **Headers** - Response headers (click to expand)

## Example: Create a Resource

1. Select `POST /v2/resources`
2. Enter the request body:
   ```json
   {
     "name": "My New Resource",
     "type": "compute",
     "region": "us-east-1"
   }
   ```
3. Click **Execute**
4. View the response with the new resource's ID

## Example: List Users

1. Select `GET /v2/users`
2. Optionally add query parameters:
   - `per_page`: 10
   - `page`: 1
3. Click **Execute**
4. Browse the paginated user list

## Tips

- Use the **Copy** button to copy cURL commands
- Check the **History** tab to replay previous requests
- Toggle **Dark Mode** for comfortable viewing
- Use **Search** to find specific endpoints quickly

## Limitations

- The console runs in the browser — CORS must be enabled on the API
- Rate limits still apply
- Webhook testing requires a public endpoint
- File uploads are not supported in the console
