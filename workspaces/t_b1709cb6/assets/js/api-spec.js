/**
 * DevPortal API Specification
 * Defines all available endpoints for the interactive API console
 */
window.API_SPEC = {
  v2: [
    {
      method: 'GET',
      path: '/v2/users',
      summary: 'List users',
      description: 'Retrieve a paginated list of all users in your organization.',
      parameters: [
        { name: 'page', type: 'number', required: false, description: 'Page number (default: 1)' },
        { name: 'per_page', type: 'number', required: false, description: 'Items per page (default: 20, max: 100)' },
        { name: 'status', type: 'string', required: false, description: 'Filter by status: active, inactive, all' }
      ]
    },
    {
      method: 'GET',
      path: '/v2/users/me',
      summary: 'Get current user',
      description: 'Retrieve the currently authenticated user\'s profile.',
      parameters: []
    },
    {
      method: 'GET',
      path: '/v2/users/{id}',
      summary: 'Get a user',
      description: 'Retrieve a specific user by their ID.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'User ID' }
      ]
    },
    {
      method: 'PATCH',
      path: '/v2/users/{id}',
      summary: 'Update user',
      description: 'Update a user\'s profile information.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'User ID' }
      ],
      requestBody: '{\n  "name": "Updated Name",\n  "email": "updated@example.com",\n  "status": "active"\n}'
    },
    {
      method: 'DELETE',
      path: '/v2/users/{id}',
      summary: 'Delete user',
      description: 'Permanently delete a user account.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'User ID' }
      ]
    },
    {
      method: 'GET',
      path: '/v2/resources',
      summary: 'List resources',
      description: 'Retrieve a paginated list of all resources.',
      parameters: [
        { name: 'page', type: 'number', required: false, description: 'Page number' },
        { name: 'per_page', type: 'number', required: false, description: 'Items per page' },
        { name: 'type', type: 'string', required: false, description: 'Filter by resource type' },
        { name: 'status', type: 'string', required: false, description: 'Filter by status' },
        { name: 'region', type: 'string', required: false, description: 'Filter by region' }
      ]
    },
    {
      method: 'POST',
      path: '/v2/resources',
      summary: 'Create resource',
      description: 'Create a new resource.',
      parameters: [],
      requestBody: '{\n  "name": "My Resource",\n  "type": "compute",\n  "region": "us-east-1",\n  "metadata": {}\n}'
    },
    {
      method: 'GET',
      path: '/v2/resources/{id}',
      summary: 'Get resource',
      description: 'Retrieve a specific resource by ID.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Resource ID' }
      ]
    },
    {
      method: 'PUT',
      path: '/v2/resources/{id}',
      summary: 'Update resource',
      description: 'Update an existing resource.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Resource ID' }
      ],
      requestBody: '{\n  "name": "Updated Resource",\n  "status": "active",\n  "metadata": {}\n}'
    },
    {
      method: 'DELETE',
      path: '/v2/resources/{id}',
      summary: 'Delete resource',
      description: 'Permanently delete a resource.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Resource ID' }
      ]
    },
    {
      method: 'GET',
      path: '/v2/webhooks',
      summary: 'List webhooks',
      description: 'Retrieve all registered webhooks.',
      parameters: [
        { name: 'active', type: 'string', required: false, description: 'Filter by active status: true, false' }
      ]
    },
    {
      method: 'POST',
      path: '/v2/webhooks',
      summary: 'Create webhook',
      description: 'Register a new webhook endpoint.',
      parameters: [],
      requestBody: '{\n  "url": "https://example.com/webhooks",\n  "events": ["resource.created", "resource.updated"],\n  "secret": "your-secret",\n  "active": true\n}'
    },
    {
      method: 'GET',
      path: '/v2/webhooks/{id}',
      summary: 'Get webhook',
      description: 'Retrieve a specific webhook by ID.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Webhook ID' }
      ]
    },
    {
      method: 'PATCH',
      path: '/v2/webhooks/{id}',
      summary: 'Update webhook',
      description: 'Update a webhook configuration.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Webhook ID' }
      ],
      requestBody: '{\n  "events": ["resource.created"],\n  "active": true\n}'
    },
    {
      method: 'DELETE',
      path: '/v2/webhooks/{id}',
      summary: 'Delete webhook',
      description: 'Remove a webhook registration.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Webhook ID' }
      ]
    },
    {
      method: 'POST',
      path: '/v2/webhooks/{id}/test',
      summary: 'Test webhook',
      description: 'Send a test event to your webhook endpoint.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Webhook ID' }
      ],
      requestBody: '{\n  "event": "resource.created"\n}'
    }
  ],
  v1: [
    {
      method: 'GET',
      path: '/v1/users',
      summary: 'List users (v1)',
      description: 'Retrieve a paginated list of users.',
      parameters: [
        { name: 'page', type: 'number', required: false, description: 'Page number' },
        { name: 'limit', type: 'number', required: false, description: 'Items per page' }
      ]
    },
    {
      method: 'GET',
      path: '/v1/users/{id}',
      summary: 'Get user (v1)',
      description: 'Retrieve a specific user by ID.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'User ID' }
      ]
    },
    {
      method: 'GET',
      path: '/v1/resources',
      summary: 'List resources (v1)',
      description: 'Retrieve a paginated list of resources.',
      parameters: [
        { name: 'page', type: 'number', required: false, description: 'Page number' },
        { name: 'limit', type: 'number', required: false, description: 'Items per page' }
      ]
    },
    {
      method: 'POST',
      path: '/v1/resources',
      summary: 'Create resource (v1)',
      description: 'Create a new resource.',
      parameters: [],
      requestBody: '{\n  "name": "My Resource",\n  "type": "server"\n}'
    },
    {
      method: 'GET',
      path: '/v1/resources/{id}',
      summary: 'Get resource (v1)',
      description: 'Retrieve a specific resource by ID.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Resource ID' }
      ]
    },
    {
      method: 'DELETE',
      path: '/v1/resources/{id}',
      summary: 'Delete resource (v1)',
      description: 'Delete a resource.',
      parameters: [
        { name: 'id', type: 'string', required: true, description: 'Resource ID' }
      ]
    }
  ]
};
