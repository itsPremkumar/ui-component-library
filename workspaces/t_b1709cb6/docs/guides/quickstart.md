# Quick Start Guide

Get up and running with DevPortal in under 5 minutes.

## Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- A local web server (optional, for development)
- Git (optional, for cloning)

## Step 1: Clone or Download

```bash
git clone https://github.com/itsPremkumar/developer-portal.git
cd developer-portal
```

Or simply download the ZIP from GitHub and extract it.

## Step 2: Open the Portal

### Option A: Direct Open

Just double-click `index.html` — it opens in your browser immediately.

### Option B: Local Server

For the best experience (some features require HTTP):

=== "Python"
    ```bash
    python -m http.server 3000
    ```

=== "Node.js"
    ```bash
    npx serve .
    ```

=== "PHP"
    ```bash
    php -S localhost:3000
    ```

=== "Docsify CLI"
    ```bash
    npm install -g docsify-cli
    docsify serve .
    ```

Then open `http://localhost:3000`.

## Step 3: Navigate

Use the **sidebar** on the left to navigate between:

- **Guides** - Step-by-step tutorials
- **API Reference** - Complete endpoint documentation
- **API Console** - Interactive testing tool

Use the **search bar** (top-right) to find anything instantly.

## Step 4: Test an API Endpoint

1. Go to the **API Console** page
2. Select an API version (v1 or v2)
3. Choose an endpoint from the dropdown
4. Fill in any parameters
5. Click **Execute**

## Next Steps

- Read the [Installation Guide](installation.md) for production setup
- Explore the [API Reference](../api/README.md)
- Learn about [Authentication](../api/v2/authentication.md)
- Check the [Configuration Guide](configuration.md)
